import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from resolver import Resolver, FilterDomainInfo


class ResolverTests(unittest.TestCase):
    def setUp(self):
        self.resolver = Resolver(".")

    def test_analysis_ipv6(self):
        address, sub = self.resolver._Resolver__analysis("2606:4700:4700::1111")
        self.assertEqual(address, "2606:4700:4700::1111")
        self.assertEqual(sub, "")

    def test_analysis_rejects_reserved_ipv6(self):
        with self.assertRaisesRegex(Exception, "not domain or public ip"):
            self.resolver._Resolver__analysis("2001:db8::1")

    def test_filter_target_domain(self):
        _, info = self.resolver._Resolver__resolveFilterDomain("||Example.COM^$script")
        self.assertIsInstance(info, FilterDomainInfo)
        self.assertEqual(info.source, "target")
        self.assertIn("example.com", info.domains)

    def test_filter_context_multi_domain(self):
        _, info = self.resolver._Resolver__resolveFilterDomain("example.com,example.edu##.ad")
        self.assertEqual(info.source, "context")
        self.assertIn("example.com", info.domains)
        self.assertIn("example.edu", info.domains)

    def test_filter_context_domain_option(self):
        _, info = self.resolver._Resolver__resolveFilterDomain("||/ads.js$domain=example.com|~foo.com")
        self.assertEqual(info.source, "context")
        self.assertIn("example.com", info.domains)
        self.assertNotIn("foo.com", info.domains)

    def test_filter_negative_only_context(self):
        _, info = self.resolver._Resolver__resolveFilterDomain("~example.com##.ad")
        self.assertEqual(info.source, "none")
        self.assertEqual(len(info.domains), 0)


if __name__ == "__main__":
    unittest.main()
