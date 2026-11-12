#!/usr/bin/env python3
"""Build a self-contained NuGet runtime native payload for C# (.NET 8+)."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

CSHARP_DIR = Path(__file__).resolve().parent
REPO_ROOT = CSHARP_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import bundle_native_package  # noqa: E402
import generate_swig_bindings  # noqa: E402
import prepare_purpleair_api_source  # noqa: E402
import prepare_sqlite3_amalgamation  # noqa: E402


def _current_rid() -> str:
    machine = platform.machine().lower()
    if sys.platform == "darwin":
        return "osx-arm64" if "arm" in machine or "aarch64" in machine else "osx-x64"
    if sys.platform == "win32":
        if "arm" in machine:
            return "win-arm64"
        return "win-x64" if "64" in machine else "win-x86"
    return "linux-arm64" if "arm" in machine or "aarch64" in machine else "linux-x64"


def main() -> int:
    prepare_sqlite3_amalgamation.ensure_sqlite3_amalgamation()
    prepare_purpleair_api_source.ensure_purpleair_api_source()
    rc = generate_swig_bindings.main(
        ["--languages", "csharp", "--out-dir", str(CSHARP_DIR / "generated")]
    )
    if rc != 0:
        return rc

    build_dir = CSHARP_DIR / "build-native"
    subprocess.run(
        [
            "cmake",
            "-B",
            str(build_dir),
            "-S",
            str(CSHARP_DIR),
            "-DCMAKE_BUILD_TYPE=Release",
        ],
        check=True,
    )
    jobs = str(os.cpu_count() or 4)
    subprocess.run(
        ["cmake", "--build", str(build_dir), "--config", "Release", "--parallel", jobs],
        check=True,
    )

    rid = _current_rid()
    native_dir = CSHARP_DIR / "runtimes" / rid / "native"
    native_dir.mkdir(parents=True, exist_ok=True)

    candidates = (
        list(build_dir.rglob("libpurpleair_data_logger_csharp.dylib"))
        + list(build_dir.rglob("libpurpleair_data_logger_csharp.so"))
        + list(build_dir.rglob("purpleair_data_logger_csharp.dll"))
    )
    if not candidates:
        raise FileNotFoundError(
            f"Built native P/Invoke library not found under {build_dir}"
        )

    src_lib = candidates[0]
    dst_lib = native_dir / src_lib.name
    dst_lib.write_bytes(src_lib.read_bytes())

    report = bundle_native_package.bundle_artifact(dst_lib, libs_dir=native_dir)
    if not report["ok"]:
        raise RuntimeError(f"C# native library has unbundled dependencies: {report}")
    print(f"Self-contained C# native runtime ready at: {native_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
