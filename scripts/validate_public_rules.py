import os
import re
import sys


RAW_RULE_PATTERN = re.compile(
    r"https://raw\.githubusercontent\.com/"
    r"Aethersailor/adblockfilters-modified/main/rules/([^)\s|]+)"
)


def referenced_rule_paths(readme_path: str) -> list:
    with open(readme_path, "r", encoding="utf-8") as f:
        names = sorted(set(RAW_RULE_PATTERN.findall(f.read())))
    return [os.path.join("rules", name) for name in names]


def validate_paths(paths: list) -> list:
    errors = []
    for path in paths:
        if not os.path.isfile(path):
            errors.append("missing public rule: %s" % path)
            continue
        if os.path.getsize(path) <= 0:
            errors.append("empty public rule: %s" % path)
    return errors


def main() -> int:
    paths = referenced_rule_paths("README.md")
    if not paths:
        print("error: no public rule links found in README.md")
        return 1
    errors = validate_paths(paths)
    for error in errors:
        print("error: %s" % error)
    if errors:
        return 1
    print("validated %d public rule paths" % len(paths))
    return 0


if __name__ == "__main__":
    sys.exit(main())
