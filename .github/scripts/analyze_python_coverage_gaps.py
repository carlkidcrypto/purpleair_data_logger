#!/usr/bin/env python3
"""Analyze Python source coverage gaps for the purpleair_data_logger project.

This script statically inspects the Python source files in ``purpleair_data_logger/``
and the corresponding test files in ``tests/`` to identify which callable
branches (methods, functions) lack direct unit-test references.

Usage:
    python3 .github/scripts/analyze_python_coverage_gaps.py
    python3 .github/scripts/analyze_python_coverage_gaps.py --src purpleair_data_logger --tests tests
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]


def collect_callables(source_path: Path) -> List[str]:
    """Return a list of function/method names defined in source_path."""
    try:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        print(f"  [WARN] SyntaxError in {source_path}: {exc}", file=sys.stderr)
        return []

    names: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)
    return sorted(set(names))


def collect_conditional_markers(source_path: Path) -> List[str]:
    """Identify lines with pragma: no cover."""
    markers: List[str] = []
    for lineno, line in enumerate(
        source_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if "pragma: no cover" in line:
            markers.append(f"line {lineno}: {line.strip()}")
    return markers


def collect_test_references(test_dir: Path) -> Dict[str, Set[str]]:
    """Build a mapping from test filename to set of identifier tokens."""
    refs: Dict[str, Set[str]] = {}
    for test_file in sorted(test_dir.glob("test_*.py")):
        text = test_file.read_text(encoding="utf-8")
        tokens = set(re.findall(r"[A-Za-z_]\w*", text))
        refs[test_file.name] = tokens
    return refs


def find_uncovered_callables(
    callables: List[str],
    test_refs: Dict[str, Set[str]],
    skip_private: bool = True,
) -> Tuple[List[str], List[str]]:
    """Partition callables into covered/uncovered based on test_refs."""
    all_tokens: Set[str] = set()
    for tokens in test_refs.values():
        all_tokens |= tokens

    covered: List[str] = []
    uncovered: List[str] = []
    for name in callables:
        if skip_private and name.startswith("__") and name.endswith("__"):
            covered.append(name)
            continue
        if name in all_tokens:
            covered.append(name)
        else:
            uncovered.append(name)
    return covered, uncovered


def report_file(
    source_path: Path,
    callables: List[str],
    covered: List[str],
    uncovered: List[str],
    no_cover_markers: List[str],
) -> None:
    """Print formatted gap report for a single source file."""
    total = len(callables)
    cov_count = len(covered)
    unc_count = len(uncovered)
    pct = (cov_count / total * 100) if total > 0 else 100.0

    status = "✅" if unc_count == 0 else "⚠️ "
    print(f"\n{status}  {source_path.name}  ({cov_count}/{total} — {pct:.0f}%)")

    if uncovered:
        print("  Potentially uncovered callables:")
        for name in uncovered:
            print(f"    - {name}")

    if no_cover_markers:
        print("  Lines with 'pragma: no cover':")
        for marker in no_cover_markers:
            print(f"    {marker}")


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Analyze Python coverage gaps for purpleair_data_logger."
    )
    parser.add_argument(
        "--src",
        default="purpleair_data_logger",
        help="Path to Python source directory (default: 'purpleair_data_logger').",
    )
    parser.add_argument(
        "--tests",
        default="tests",
        help="Path to test directory (default: 'tests').",
    )
    parser.add_argument(
        "--skip-dunders",
        action="store_true",
        default=True,
        help="Treat dunder methods as covered (default: True).",
    )
    args = parser.parse_args()

    src_dir = REPO_ROOT / args.src
    test_dir = REPO_ROOT / args.tests

    if not src_dir.is_dir():
        print(f"ERROR: Source directory not found: {src_dir}", file=sys.stderr)
        return 1
    if not test_dir.is_dir():
        print(f"ERROR: Test directory not found: {test_dir}", file=sys.stderr)
        return 1

    print(f"Source package : {src_dir}")
    print(f"Test directory : {test_dir}")

    test_refs = collect_test_references(test_dir)
    print(f"Test files found: {len(test_refs)}")

    source_files = sorted(src_dir.glob("*.py"))
    overall_has_gaps = False

    for src_file in source_files:
        callables = collect_callables(src_file)
        no_cover = collect_conditional_markers(src_file)
        covered, uncovered = find_uncovered_callables(
            callables, test_refs, skip_private=args.skip_dunders
        )
        report_file(src_file, callables, covered, uncovered, no_cover)
        if uncovered:
            overall_has_gaps = True

    print("\n" + "=" * 60)
    if overall_has_gaps:
        print("Coverage gaps detected — see report above.")
        return 1
    else:
        print("No coverage gaps detected.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
