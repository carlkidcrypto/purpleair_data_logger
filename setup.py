#!/usr/bin/env python3
"""Setup script for purpleair_data_logger with self-contained SWIG 4.x C++17 bindings."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py

if sys.platform == "darwin":
    os.environ.setdefault("ARCHFLAGS", f"-arch {platform.machine()}")
    mac_ver = platform.mac_ver()[0]
    if mac_ver:
        major = mac_ver.split(".")[0]
        if major.isdigit() and int(major) >= 11:
            os.environ["MACOSX_DEPLOYMENT_TARGET"] = f"{major}.0"
    else:
        os.environ["MACOSX_DEPLOYMENT_TARGET"] = "11.0"

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))

import bundle_native_package  # noqa: E402
import prepare_purpleair_api_source  # noqa: E402
import prepare_sqlite3_amalgamation  # noqa: E402


def _has_swig() -> bool:
    if os.environ.get("PURPLEAIR_PURE_PYTHON", "").strip() == "1":
        return False
    return shutil.which("swig") is not None


def _detect_pkg_config(pkg: str) -> tuple[list[str], list[str], list[str]]:
    include_dirs: list[str] = []
    library_dirs: list[str] = []
    libraries: list[str] = []
    try:
        cflags = subprocess.check_output(
            ["pkg-config", "--cflags", pkg], stderr=subprocess.DEVNULL, text=True
        ).split()
        libs = subprocess.check_output(
            ["pkg-config", "--libs", pkg], stderr=subprocess.DEVNULL, text=True
        ).split()
        for flag in cflags:
            if flag.startswith("-I"):
                include_dirs.append(flag[2:])
        for flag in libs:
            if flag.startswith("-L"):
                library_dirs.append(flag[2:])
            elif flag.startswith("-l"):
                libraries.append(flag[2:])
    except Exception:
        pass
    return include_dirs, library_dirs, libraries


def _configure_extension() -> list[Extension]:
    if not _has_swig():
        return []

    sqlite_dir = prepare_sqlite3_amalgamation.ensure_sqlite3_amalgamation(ROOT)
    sources = [
        "src/purpleair_data_logger_wrap.cxx",
        "src/version.cpp",
        "src/json_utils.cpp",
        "src/datatypes.cpp",
        "src/config.cpp",
        "src/purpleair_poller.cpp",
        "src/csv_sink.cpp",
        "src/jsonl_sink.cpp",
        "src/sqlite_sink.cpp",
        "src/psql_sink.cpp",
        "src/prometheus_sink.cpp",
        "src/sink_inspector.cpp",
        "src/data_logger.cpp",
        "src/cli_runner.cpp",
        str(sqlite_dir.relative_to(ROOT) / "sqlite3.c"),
    ]
    include_dirs = ["include", str(sqlite_dir.relative_to(ROOT))]
    library_dirs: list[str] = []
    libraries: list[str] = []
    define_macros: list[tuple[str, str | None]] = [
        ("PURPLEAIR_DL_HAVE_SQLITE3", "1"),
        ("PURPLEAIR_DL_EMBEDDED_SQLITE3", "1"),
        ("SQLITE_THREADSAFE", "1"),
        ("SQLITE_ENABLE_FTS5", "1"),
        ("SQLITE_ENABLE_JSON1", "1"),
        ("SQLITE_OMIT_LOAD_EXTENSION", "1"),
    ]

    # Integrate purpleair_api C++17 layer if available and libcurl is present
    try:
        pa_root = prepare_purpleair_api_source.ensure_purpleair_api_source(ROOT)
    except Exception:
        pa_root = None

    if (
        pa_root is not None
        and (pa_root / "swig" / "src" / "PurpleAirAPI.cpp").is_file()
    ):
        curl_inc, curl_libdirs, curl_libs = _detect_pkg_config("libcurl")
        has_curl = (
            bool(curl_libs)
            or sys.platform == "darwin"
            or Path("/usr/include/curl/curl.h").is_file()
            or Path("/usr/include/x86_64-linux-gnu/curl/curl.h").is_file()
        )
        if has_curl:
            include_dirs.append(str(pa_root / "swig" / "include"))
            include_dirs.extend(curl_inc)
            library_dirs.extend(curl_libdirs)
            libraries.extend(curl_libs if curl_libs else ["curl"])
            sources.extend(
                [
                    str(pa_root / "swig" / "src" / "PurpleAirAPI.cpp"),
                    str(pa_root / "swig" / "src" / "PurpleAirAPIHelpers.cpp"),
                    str(pa_root / "swig" / "src" / "PurpleAirReadAPI.cpp"),
                    str(pa_root / "swig" / "src" / "PurpleAirWriteAPI.cpp"),
                    str(pa_root / "swig" / "src" / "PurpleAirLocalAPI.cpp"),
                ]
            )
            define_macros.append(("PURPLEAIR_DL_HAVE_PURPLEAIR_API", "1"))

    extra_compile_args: list[str] = []
    extra_link_args: list[str] = []
    if sys.platform == "win32":
        libraries.append("ws2_32")
        extra_compile_args.extend(["/std:c++17", "/EHsc", "/MP"])
    else:
        extra_compile_args.extend(["-std=c++17", "-O2"])
        if sys.platform == "darwin":
            extra_compile_args.append("-mmacosx-version-min=11.0")
            extra_link_args.extend(
                ["-mmacosx-version-min=11.0", "-Wl,-rpath,@loader_path/.dylibs"]
            )
        else:
            extra_link_args.append("-Wl,-rpath,$ORIGIN/libs")

    return [
        Extension(
            "purpleair_data_logger._purpleair_data_logger",
            sources=sources,
            include_dirs=include_dirs,
            library_dirs=library_dirs,
            libraries=libraries,
            define_macros=define_macros,
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
            language="c++",
        )
    ]


class SwigBuildExt(build_ext):
    """Run SWIG 4.x before compiling the C++17 extension and bundle non-OS shared libraries."""

    def run(self) -> None:
        if not self.extensions:
            return
        swig_bin = shutil.which("swig") or "swig"
        wrap_out = ROOT / "src" / "purpleair_data_logger_wrap.cxx"
        py_out_dir = ROOT / "purpleair_data_logger"
        iface = ROOT / "interface" / "purpleair_data_logger.i"

        cmd = [
            swig_bin,
            "-c++",
            "-python",
            "-threads",
            "-module",
            "purpleair_data_logger_swig",
            "-interface",
            "_purpleair_data_logger",
            f"-I{ROOT / 'include'}",
            f"-I{ROOT / 'interface'}",
            "-outdir",
            str(py_out_dir),
            "-o",
            str(wrap_out),
            str(iface),
        ]
        subprocess.run(cmd, check=True)
        super().run()

        for ext in self.extensions:
            ext_path = Path(self.get_ext_fullpath(ext.name)).resolve()
            if ext_path.is_file():
                try:
                    bundle_native_package.bundle_artifact(ext_path)
                except Exception as exc:
                    print(f"[setup.py] Notice during native bundling: {exc}")

    def build_extensions(self) -> None:
        ct = self.compiler.compiler_type
        if ct == "unix":
            orig_compile = self.compiler._compile

            def _custom_compile(obj, src, ext, cc_args, extra_postargs, pp_opts):
                post = list(extra_postargs or [])
                if str(src).endswith(".c"):
                    post = [a for a in post if not a.startswith("-std=c++")]
                return orig_compile(obj, src, ext, cc_args, post, pp_opts)

            self.compiler._compile = _custom_compile
        super().build_extensions()


class SwigBuildPy(build_py):
    """Ensure SWIG Python wrapper module exists before packaging Python files."""

    def run(self) -> None:
        if _has_swig():
            self.run_command("build_ext")
        super().run()


setup(
    ext_modules=_configure_extension(),
    cmdclass={
        "build_ext": SwigBuildExt,
        "build_py": SwigBuildPy,
    },
)
