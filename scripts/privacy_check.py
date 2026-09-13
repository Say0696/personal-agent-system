#!/usr/bin/env python3
"""Fail if staged/public files contain local memory or obvious private paths."""
from pathlib import Path
import re
import subprocess
import sys


def main() -> int:
    files = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
    bad_names = {"memory/rules.yaml"}
    bad_patterns = [re.compile(r"[A-Za-z]:[\\/]Users[\\/]", re.I), re.compile(r"gho_[A-Za-z0-9_\-]{20,}")]
    problems = []
    for name in files:
        if name.replace("\\", "/") in bad_names:
            problems.append(f"private memory file staged: {name}")
            continue
        path = Path(name)
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in bad_patterns:
            if pattern.search(text):
                problems.append(f"private-looking content in {name}: {pattern.pattern}")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(f"privacy check passed ({len(files)} staged paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
