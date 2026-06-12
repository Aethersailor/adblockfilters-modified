import asyncio
import os
import sys
import unittest
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import AsyncMock, Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from blacklist import (
    BlackList,
    DNS_STATUS_ERROR,
    DNS_STATUS_NXDOMAIN,
    DNS_STATUS_SUCCESS,
    DNS_STATUS_TIMEOUT,
    _harden_regexp,
)


def classify_cn_suffix(domain, ip_list):
    return domain, domain.endswith(".cn")


class BlackListTests(unittest.TestCase):
    def make_blacklist(self):
        blacklist = BlackList.__new__(BlackList)
        blacklist._BlackList__dns_stats = Counter()
        blacklist._BlackList__dns_retries = 1
        return blacklist

    def test_harden_nested_subdomain_regexp(self):
        pattern = r"^(.+\.)*zh\.okaapps\.com$"
        self.assertEqual(
            _harden_regexp(pattern),
            r"^(?:[^.]+\.)*zh\.okaapps\.com$",
        )

    def test_terminal_dns_failure_is_not_retried(self):
        blacklist = self.make_blacklist()
        resolver = AsyncMock(return_value=([], DNS_STATUS_NXDOMAIN))
        blacklist._BlackList__resolve = resolver

        result = asyncio.run(
            blacklist._BlackList__pingx(
                object(),
                "does-not-exist.com",
                asyncio.Semaphore(1),
            )
        )

        self.assertEqual(result, ("does-not-exist.com", [], DNS_STATUS_NXDOMAIN))
        self.assertEqual(resolver.await_count, 1)
        self.assertEqual(blacklist._BlackList__dns_stats["primary_retries"], 0)

    def test_transient_dns_failure_has_bounded_retry(self):
        blacklist = self.make_blacklist()
        resolver = AsyncMock(
            side_effect=[
                ([], DNS_STATUS_TIMEOUT),
                (["203.0.113.10"], DNS_STATUS_SUCCESS),
            ]
        )
        blacklist._BlackList__resolve = resolver

        result = asyncio.run(
            blacklist._BlackList__pingx(
                object(),
                "example.com",
                asyncio.Semaphore(1),
            )
        )

        self.assertEqual(
            result,
            ("example.com", ["203.0.113.10"], DNS_STATUS_SUCCESS),
        )
        self.assertEqual(resolver.await_count, 2)
        self.assertEqual(blacklist._BlackList__dns_stats["primary_retries"], 1)

    def test_transient_failures_use_previous_classification(self):
        blacklist = self.make_blacklist()
        domain_dict = {
            "resolved.cn": (["203.0.113.10"], DNS_STATUS_SUCCESS),
            "old-black.example": ([], DNS_STATUS_TIMEOUT),
            "old-china.example": ([], DNS_STATUS_ERROR),
            "unknown.example": ([], DNS_STATUS_TIMEOUT),
            "invalid.example": ([], DNS_STATUS_NXDOMAIN),
        }

        with ThreadPoolExecutor(max_workers=2) as executor:
            black, china = blacklist._BlackList__classifyBatch(
                domain_dict,
                {"old-black.example"},
                {"old-china.example"},
                classify_cn_suffix,
                executor,
            )

        self.assertEqual(
            black,
            ["old-black.example", "invalid.example"],
        )
        self.assertEqual(
            china,
            {"resolved.cn", "old-china.example"},
        )
        self.assertEqual(
            blacklist._BlackList__dns_stats["fallback_unclassified"],
            1,
        )

    def test_rule_count_anomaly_stops_generation(self):
        blacklist = self.make_blacklist()
        blacklist._BlackList__blacklistFile = "unused"
        blacklist._BlackList__safe_write_list = Mock(
            side_effect=RuntimeError("black list anomaly")
        )

        with self.assertRaisesRegex(RuntimeError, "black list anomaly"):
            blacklist._BlackList__generateBlackList(["example.com"])


if __name__ == "__main__":
    unittest.main()
