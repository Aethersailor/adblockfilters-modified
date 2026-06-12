import os
import subprocess
import sys


FILES = [
    "rules/adblockdns.txt",
    "rules/adblockdnslite.txt",
    "rules/adblockdomain.txt",
    "rules/adblockdomainlite.txt",
    "rules/adblockfilters.txt",
    "rules/adblockfilterslite.txt",
    "rules/adblockmihomo.yaml",
    "rules/adblockmihomolite.yaml",
    "rules/adblockrouteros.txt",
    "rules/adblockrouteroslite.txt",
    "rules/adblockrouterosadlist.txt",
    "rules/adblockrouterosadlistlite.txt",
    "rules/adblocksingbox.json",
    "rules/adblocksingboxlite.json",
]
MIN_RATIO = 0.7
MAX_RATIO = 1.5
MIN_ABS = 10000


def count_binary_lines(stream) -> int:
    return sum(1 for line in stream if line.strip())


def get_prev_count(path: str):
    process = subprocess.Popen(
        ["git", "show", "HEAD:%s" % path],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if process.stdout is None:
        return None
    count = count_binary_lines(process.stdout)
    return count if process.wait() == 0 else None


def get_cur_count(path: str):
    try:
        with open(path, "rb") as f:
            return count_binary_lines(f)
    except OSError:
        return None


def is_anomalous(new_count: int, old_count: int) -> bool:
    if old_count is None or new_count is None:
        return False
    if old_count < 1000:
        return False
    diff = abs(new_count - old_count)
    if diff < MIN_ABS:
        return False
    ratio = new_count / old_count if old_count else 1
    return ratio < MIN_RATIO or ratio > MAX_RATIO


def main() -> int:
    anomalies = []
    for path in FILES:
        old_count = get_prev_count(path)
        new_count = get_cur_count(path)
        if old_count is None or new_count is None:
            continue
        if is_anomalous(new_count, old_count):
            print(
                "warning: rule count anomaly: %s old=%d new=%d"
                % (path, old_count, new_count)
            )
            anomalies.append(path)
    if anomalies:
        if os.environ.get("ALLOW_RULE_COUNT_ANOMALY", "").lower() in {
            "1",
            "true",
            "yes",
        }:
            print("warning: rule count anomalies explicitly allowed")
            return 0
        print("error: rule count anomalies detected; refusing to publish")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
