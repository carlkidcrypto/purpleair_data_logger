#!/usr/bin/env python3
"""Download and verify the public-domain SQLite3 C amalgamation for self-contained builds.

Provisioning SQLite3 as a single-file C amalgamation (sqlite3.c + sqlite3.h) eliminates
runtime shared-library dependencies across Linux, macOS, and Windows for all 4 SWIG
target languages (Python, JavaScript/Node.js, C#, and Go).
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

SQLITE_YEAR = "2025"
SQLITE_VERSION_FOLDER = "sqlite-amalgamation-3490100"
SQLITE_ZIP_NAME = f"{SQLITE_VERSION_FOLDER}.zip"
SQLITE_URL = f"https://www.sqlite.org/{SQLITE_YEAR}/{SQLITE_ZIP_NAME}"
SQLITE_SHA256 = "e7a2ef6ebce2fbffbd1ceb2fdbe4fd27c3d3f321ec332d2d29a4f8a22f3c4223"


def ensure_sqlite3_amalgamation(repo_root: Path | None = None) -> Path:
    """Ensure third_party/sqlite3/{sqlite3.c,sqlite3.h} exist and return the directory."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent

    dest_dir = repo_root / "third_party" / "sqlite3"
    c_file = dest_dir / "sqlite3.c"
    h_file = dest_dir / "sqlite3.h"

    if c_file.is_file() and h_file.is_file():
        return dest_dir

    # Also check if sibling ezsnmp_data_logger already downloaded it locally to save network round-trip
    sibling_dir = repo_root.parent / "ezsnmp_data_logger" / "third_party" / "sqlite3"
    if (sibling_dir / "sqlite3.c").is_file() and (sibling_dir / "sqlite3.h").is_file():
        dest_dir.mkdir(parents=True, exist_ok=True)
        for fname in ("sqlite3.c", "sqlite3.h", "sqlite3ext.h"):
            src = sibling_dir / fname
            if src.is_file():
                shutil.copy2(src, dest_dir / fname)
        return dest_dir

    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / SQLITE_ZIP_NAME

    print(f"[sqlite3] Downloading {SQLITE_URL} ...")
    req = urllib.request.Request(
        SQLITE_URL,
        headers={"User-Agent": "purpleair_data_logger-build/1.0"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp, open(zip_path, "wb") as out:
        shutil.copyfileobj(resp, out)

    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    if digest != SQLITE_SHA256:
        zip_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"SQLite3 amalgamation SHA-256 mismatch: expected {SQLITE_SHA256}, got {digest}"
        )

    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in ("sqlite3.c", "sqlite3.h", "sqlite3ext.h"):
            member = f"{SQLITE_VERSION_FOLDER}/{name}"
            with zf.open(member) as src, open(dest_dir / name, "wb") as dst:
                shutil.copyfileobj(src, dst)

    zip_path.unlink(missing_ok=True)
    print(f"[sqlite3] Amalgamation ready at {dest_dir}")
    return dest_dir


if __name__ == "__main__":
    try:
        path = ensure_sqlite3_amalgamation()
        print(str(path))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
