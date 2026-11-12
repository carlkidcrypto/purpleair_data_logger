#!/usr/bin/env python3
"""Build utility helpers for parallel compilation and object caching."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path


def resolve_build_jobs(
    explicit_jobs: int | bool | None = None, cpu_count: int | None = None
) -> int:
    """Resolve the number of worker threads to use for parallel compilation.

    Precedence:
    1. ``PURPLEAIR_BUILD_JOBS`` or ``EZSNMP_BUILD_JOBS`` environment variable
       (positive integer or ``"auto"``).
    2. *explicit_jobs* from ``build_ext --parallel`` / ``-j`` (``True`` -> ``cpus - 1``).
    3. Default: ``max(1, cpus - 1)`` so builds leave one core free on local dev machines.
    """
    cpus = cpu_count if cpu_count is not None else (os.cpu_count() or 1)
    default_jobs = max(1, cpus - 1)

    raw_env = os.environ.get("PURPLEAIR_BUILD_JOBS") or os.environ.get(
        "EZSNMP_BUILD_JOBS"
    )
    if raw_env is not None and raw_env.strip():
        cleaned = raw_env.strip().lower()
        if cleaned == "auto":
            return max(1, cpus)
        try:
            parsed = int(cleaned)
        except ValueError as exc:
            raise ValueError(
                f"Invalid PURPLEAIR_BUILD_JOBS={raw_env!r}; expected a positive integer or 'auto'."
            ) from exc
        if parsed < 1:
            raise ValueError(
                f"Invalid PURPLEAIR_BUILD_JOBS={raw_env!r}; value must be >= 1."
            )
        return parsed

    if explicit_jobs is True:
        return default_jobs
    if explicit_jobs not in (None, False):
        try:
            parsed = int(explicit_jobs)
            if parsed >= 1:
                return parsed
        except ValueError:
            pass

    return default_jobs


def is_up_to_date(outputs: list[str], inputs: list[str]) -> bool:
    """Return True when all *outputs* exist and are strictly newer than all *inputs*."""
    if not outputs:
        return False
    try:
        output_mtimes = [
            os.path.getmtime(out) for out in outputs if os.path.isfile(out)
        ]
        if len(output_mtimes) != len(outputs):
            return False
        if not inputs:
            return True
        input_mtimes = [os.path.getmtime(inp) for inp in inputs if os.path.isfile(inp)]
        if len(input_mtimes) != len(inputs):
            return False
        return min(output_mtimes) > max(input_mtimes)
    except OSError:
        return False


def is_python_independent_source(src_path: str) -> bool:
    """Return True for pure C/C++ sources that do not include Python headers."""
    base = os.path.basename(src_path)
    return not (base.startswith("purpleair_data_logger_wrap") or "_wrap." in base)


def collect_files_with_suffixes(
    directories: list[str | Path], suffixes: tuple[str, ...]
) -> list[str]:
    """Collect sorted file paths matching *suffixes* recursively under *directories*."""
    collected = []
    for directory in directories:
        root_path = Path(directory)
        if not root_path.is_dir():
            continue
        for candidate in root_path.rglob("*"):
            if candidate.is_file() and candidate.suffix in suffixes:
                collected.append(str(candidate))
    return sorted(set(collected))


def _hash_file_sha256(file_path: str | Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_object_cache_key(
    src_path: str,
    header_files: list[str],
    compiler_identity: dict,
    macros: list,
    non_python_incdirs: list[str],
    extra_args: list[str],
    debug: bool,
    plat_name: str | None = None,
) -> str:
    """Compute a deterministic SHA-256 cache key for a Python-independent C/C++ object."""
    payload = {
        "plat_name": plat_name or sys.platform,
        "compiler_identity": compiler_identity,
        "macros": [list(item) for item in (macros or [])],
        "non_python_incdirs": list(non_python_incdirs or []),
        "extra_args": list(extra_args or []),
        "debug": bool(debug),
        "src_path": os.path.normpath(src_path).replace("\\", "/"),
        "src_sha256": _hash_file_sha256(src_path),
        "headers": [
            [
                os.path.normpath(hdr).replace("\\", "/"),
                _hash_file_sha256(hdr),
            ]
            for hdr in sorted(header_files)
            if os.path.isfile(hdr)
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
