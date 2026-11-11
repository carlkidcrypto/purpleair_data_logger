#!/usr/bin/env python3
"""Ensure the purpleair_api C++17 source tree is available for self-contained native compilation."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

PURPLEAIR_API_REPO_URL = "https://github.com/carlkidcrypto/purpleair_api.git"
PURPLEAIR_API_REF = os.environ.get("PURPLEAIR_API_GIT_REF", "main")


def _has_purpleair_cpp_sources(root: Path) -> bool:
    return (
        (root / "swig" / "include" / "PurpleAirAPI.h").is_file()
        and (root / "swig" / "src" / "PurpleAirAPI.cpp").is_file()
        and (root / "swig" / "src" / "PurpleAirReadAPI.cpp").is_file()
        and (root / "swig" / "src" / "PurpleAirLocalAPI.cpp").is_file()
    )


def ensure_purpleair_api_source(repo_root: Path | None = None) -> Path:
    """Locate or clone purpleair_api and return its root directory."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent

    env_dir = os.environ.get("PURPLEAIR_API_SRC_DIR", "").strip()
    candidates = []
    if env_dir:
        candidates.append(Path(env_dir))
    candidates.extend(
        [
            repo_root / "third_party" / "purpleair_api",
            repo_root.parent / "purpleair_api",
        ]
    )

    for cand in candidates:
        if _has_purpleair_cpp_sources(cand):
            return cand.resolve()

    dest_dir = repo_root / "third_party" / "purpleair_api"
    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    max_attempts = 4
    for attempt in range(1, max_attempts + 1):
        print(
            f"[purpleair_api] Cloning {PURPLEAIR_API_REPO_URL}@{PURPLEAIR_API_REF} into {dest_dir} "
            f"(attempt {attempt}/{max_attempts})..."
        )
        try:
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    PURPLEAIR_API_REF,
                    PURPLEAIR_API_REPO_URL,
                    str(dest_dir),
                ],
                check=True,
            )
            break
        except subprocess.CalledProcessError:
            shutil.rmtree(dest_dir, ignore_errors=True)
            if attempt == max_attempts:
                raise
            backoff_sec = 2**attempt
            print(f"[purpleair_api] Clone failed; retrying in {backoff_sec}s...")
            time.sleep(backoff_sec)

    if not _has_purpleair_cpp_sources(dest_dir):
        raise RuntimeError(
            f"Cloned purpleair_api at {dest_dir} is missing expected C++17 files"
        )
    return dest_dir.resolve()


if __name__ == "__main__":
    try:
        print(str(ensure_purpleair_api_source()))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
