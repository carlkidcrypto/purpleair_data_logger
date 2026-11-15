#!/usr/bin/env python3
"""Update the Sphinx landing page version list and retire superseded prerelease docs.

Usage:
    python3 .github/scripts/update_landing_versions.py [--docs-dir docs] [--index-rst sphinx_docs_build/landing/source/index.rst]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from packaging.version import Version


def parse_version(dir_name: str) -> Version:
    """Parse a versioned documentation directory name (e.g. 'html_v2026.11.3a0') into a PEP 440 Version."""
    clean = re.sub(r"^html_[vV]", "", dir_name)
    try:
        return Version(clean)
    except Exception:
        return Version("0.0.0")


def update_landing_version_list(docs_dir: Path, index_rst: Path) -> list[str]:
    """Normalize versioned doc directories, retire superseded prereleases, and update landing index.rst."""
    if not docs_dir.is_dir():
        raise FileNotFoundError(f"Documentation directory not found: {docs_dir}")
    if not index_rst.is_file():
        raise FileNotFoundError(f"Landing index.rst not found: {index_rst}")

    # Normalize any legacy html_V* directory to html_v*
    existing_names = {entry.name for entry in docs_dir.iterdir()}
    for directory in list(docs_dir.iterdir()):
        if directory.is_dir() and directory.name.startswith("html_V"):
            target_name = "html_v" + directory.name[6:]
            target = docs_dir / target_name
            if target_name not in existing_names:
                directory.rename(target)
                existing_names.discard(directory.name)
                existing_names.add(target_name)
            else:
                shutil.rmtree(directory)

    version_dirs = [
        directory
        for directory in docs_dir.iterdir()
        if directory.is_dir() and directory.name.lower().startswith("html_v")
    ]

    stable_base_versions = {
        parse_version(directory.name).base_version
        for directory in version_dirs
        if not parse_version(directory.name).is_prerelease
        and parse_version(directory.name) != Version("0.0.0")
    }

    active_dirs: list[Path] = []
    for directory in version_dirs:
        parsed = parse_version(directory.name)
        if parsed.is_prerelease and parsed.base_version in stable_base_versions:
            print(
                f"Retiring prerelease docs {directory.name} in favor of stable {parsed.base_version}"
            )
            shutil.rmtree(directory)
        else:
            active_dirs.append(directory)

    active_dirs.sort(key=lambda directory: parse_version(directory.name), reverse=True)

    entries = ["* `Latest Version <./html/index.html>`_"]
    for directory in active_dirs:
        ver_str = "v" + re.sub(r"^html_[vV]", "", directory.name)
        entries.append(f"* `{ver_str} <./{directory.name}/index.html>`_")

    content = index_rst.read_text(encoding="utf-8")
    updated, replacements = re.subn(
        r"\.\. VERSION_LIST_START\n.*?\.\. VERSION_LIST_END",
        ".. VERSION_LIST_START\n\n" + "\n".join(entries) + "\n\n.. VERSION_LIST_END",
        content,
        flags=re.DOTALL,
    )
    if replacements != 1:
        raise RuntimeError("Version list sentinels not found exactly once in index.rst")

    index_rst.write_text(updated, encoding="utf-8")
    active_names = [d.name for d in active_dirs]
    print("Updated landing/source/index.rst with versions:", active_names)
    return active_names


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Update Sphinx landing page version list and retire superseded prereleases."
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="Path to the built documentation directory (default: docs)",
    )
    parser.add_argument(
        "--index-rst",
        type=Path,
        default=Path("sphinx_docs_build/landing/source/index.rst"),
        help="Path to the landing page index.rst file",
    )
    args = parser.parse_args(argv)
    try:
        update_landing_version_list(args.docs_dir, args.index_rst)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
