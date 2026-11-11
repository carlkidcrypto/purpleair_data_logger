#!/usr/bin/env python3
"""Stage SWIG Go bindings and a self-contained native library bundle in bindings/go/lib/."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

GO_DIR = Path(__file__).resolve().parent
REPO_ROOT = GO_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import bundle_native_package  # noqa: E402
import generate_swig_bindings  # noqa: E402
import prepare_purpleair_api_source  # noqa: E402
import prepare_sqlite3_amalgamation  # noqa: E402


def main() -> int:
    prepare_sqlite3_amalgamation.ensure_sqlite3_amalgamation()
    prepare_purpleair_api_source.ensure_purpleair_api_source()
    rc = generate_swig_bindings.main(
        ["--languages", "go", "--out-dir", str(GO_DIR / "generated")]
    )
    if rc != 0:
        return rc

    build_dir = GO_DIR / "build-native"
    subprocess.run(
        [
            "cmake",
            "-B",
            str(build_dir),
            "-S",
            str(REPO_ROOT),
            "-DBUILD_SHARED_LIBS=ON",
            "-DCMAKE_BUILD_TYPE=Release",
        ],
        check=True,
    )
    subprocess.run(
        ["cmake", "--build", str(build_dir), "--config", "Release", "-j"], check=True
    )

    lib_dir = GO_DIR / "lib"
    lib_dir.mkdir(parents=True, exist_ok=True)
    candidates = (
        list(build_dir.rglob("libpurpleair_data_logger.dylib"))
        + list(build_dir.rglob("libpurpleair_data_logger.so"))
        + list(build_dir.rglob("purpleair_data_logger.dll"))
    )
    if not candidates:
        raise FileNotFoundError(f"Shared library not found in {build_dir}")

    src_lib = candidates[0]
    dst_lib = lib_dir / src_lib.name
    shutil.copy2(src_lib, dst_lib)

    report = bundle_native_package.bundle_artifact(dst_lib, libs_dir=lib_dir)
    if not report["ok"]:
        raise RuntimeError(f"Go native bundle has external dependencies: {report}")
    print(f"Self-contained Go cgo runtime ready at: {lib_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
