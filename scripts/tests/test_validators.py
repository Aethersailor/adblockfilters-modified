import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from validate_public_rules import referenced_rule_paths, validate_paths
from validate_rule_counts import is_anomalous


class ValidatorTests(unittest.TestCase):
    def test_rule_count_anomaly_requires_large_absolute_change(self):
        self.assertFalse(is_anomalous(600, 1000))
        self.assertFalse(is_anomalous(65000, 70000))
        self.assertTrue(is_anomalous(60000, 100000))
        self.assertTrue(is_anomalous(160000, 100000))

    def test_public_rule_links_are_deduplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            readme = os.path.join(directory, "README.md")
            with open(readme, "w", encoding="utf-8") as f:
                f.write(
                    "https://raw.githubusercontent.com/Aethersailor/"
                    "adblockfilters-modified/main/rules/example.txt\n"
                )
                f.write(
                    "https://raw.githubusercontent.com/Aethersailor/"
                    "adblockfilters-modified/main/rules/example.txt\n"
                )
            self.assertEqual(
                referenced_rule_paths(readme),
                [os.path.join("rules", "example.txt")],
            )

    def test_public_rule_validation_rejects_missing_and_empty_files(self):
        with tempfile.TemporaryDirectory() as directory:
            empty = os.path.join(directory, "empty.txt")
            with open(empty, "w", encoding="utf-8"):
                pass
            missing = os.path.join(directory, "missing.txt")
            errors = validate_paths([empty, missing])
            self.assertEqual(len(errors), 2)
            self.assertIn("empty public rule", errors[0])
            self.assertIn("missing public rule", errors[1])


if __name__ == "__main__":
    unittest.main()
