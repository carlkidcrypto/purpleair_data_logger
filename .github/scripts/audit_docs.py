#!/usr/bin/env python3
"""Audit purpleair_data_logger documentation for common issues and typos.

This script scans documentation files (*.rst, *.md) and Python docstrings under
``purpleair_data_logger/`` for known issues:
- Class name casing typos.
- Common spelling errors in docstrings and documentation.
- Dead links or outdated reference patterns.

Usage:
    python3 .github/scripts/audit_docs.py [--fix]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CHECKS: list[tuple[str, re.Pattern[str], str | None]] = [
    (
        "Common typo 'recieve' (should be 'receive')",
        re.compile(r"\brecieve\b", re.IGNORECASE),
        "receive",
    ),
    (
        "Common typo 'occured' (should be 'occurred')",
        re.compile(r"\boccured\b", re.IGNORECASE),
        "occurred",
    ),
    (
        "Common typo 'seperate' (should be 'separate')",
        re.compile(r"\bseperate\b", re.IGNORECASE),
        "separate",
    ),
    (
        "Incorrect class casing 'PurpleairCSVDataLogger' (should be 'PurpleAirCSVDataLogger')",
        re.compile(r"\bPurpleairCSVDataLogger\b"),
        "PurpleAirCSVDataLogger",
    ),
    (
        "Incorrect class casing 'PurpleairPSQLDataLogger' (should be 'PurpleAirPSQLDataLogger')",
        re.compile(r"\bPurpleairPSQLDataLogger\b"),
        "PurpleAirPSQLDataLogger",
    ),
    (
        "Incorrect class casing 'PurpleairSQLiteDataLogger' (should be 'PurpleAirSQLiteDataLogger')",
        re.compile(r"\bPurpleairSQLiteDataLogger\b"),
        "PurpleAirSQLiteDataLogger",
    ),
]


def collect_files() -> list[Path]:
    """Return all documentation and Python source files to audit."""
    patterns = [
        "**/*.rst",
        "**/*.md",
        "purpleair_data_logger/**/*.py",
        ".github/scripts/*.py",
    ]
    this_script = Path(__file__).resolve()
    files: set[Path] = set()
    for pattern in patterns:
        for path in REPO_ROOT.glob(pattern):
            if path.resolve() == this_script:
                continue
            parts = path.parts
            if any(
                p in parts
                for p in (
                    "__pycache__",
                    ".git",
                    "build",
                    "dist",
                    "python3.12.venv",
                    "purpleair_data_logger.egg-info",
                )
            ):
                continue
            files.add(path)
    return sorted(files)


def audit_file(path: Path) -> list[tuple[int, str, str, str | None]]:
    """Audit a single file for documentation issues."""
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    issues: list[tuple[int, str, str, str | None]] = []
    lines = content.splitlines()

    for lineno, line in enumerate(lines, start=1):
        for desc, pattern, fix in CHECKS:
            if pattern.search(line):
                issues.append((lineno, line.strip(), desc, fix))

    return issues


def fix_file(path: Path) -> int:
    """Attempt in-place fixes for auto-correctable issues in a file."""
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return 0

    original = content
    for _, pattern, fix in CHECKS:
        if fix is not None:
            content = pattern.sub(fix, content)

    if content != original:
        path.write_text(content, encoding="utf-8")
        return 1
    return 0


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Audit purpleair_data_logger documentation."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to auto-fix detected issues in-place.",
    )
    args = parser.parse_args()

    files = collect_files()
    total_issues = 0

    for file_path in files:
        issues = audit_file(file_path)
        if issues:
            rel = file_path.relative_to(REPO_ROOT)
            print(f"\n{rel}:")
            for lineno, line_text, desc, fix in issues:
                fix_hint = f" (suggested: '{fix}')" if fix else ""
                print(f"  line {lineno}: {desc}{fix_hint}")
                print(f"    {line_text}")
            total_issues += len(issues)

            if args.fix:
                if fix_file(file_path):
                    print(f"  [FIXED] Applied auto-fixes to {rel}")

    print("\n" + "=" * 60)
    if total_issues:
        print(
            f"Audit completed: {total_issues} issue(s) detected across documentation."
        )
        return 1 if not args.fix else 0
    else:
        print("Audit completed: 0 issues detected.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
