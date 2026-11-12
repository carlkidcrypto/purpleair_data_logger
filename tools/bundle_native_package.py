#!/usr/bin/env python3
"""Bundle and relocate native shared libraries so SWIG language packages are self-contained.

Supports the 4 target languages (python, javascript/Node.js N-API, csharp/.NET, go/cgo)
across Linux ($ORIGIN via patchelf), macOS (@loader_path via install_name_tool + codesign),
and Windows (side-by-side DLL bundling).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

MACOS_SYSTEM_PREFIXES = (
    "/usr/lib/",
    "/System/Library/",
    "/Library/Frameworks/Python.framework/",
    "/Applications/Xcode.app/",
)

LINUX_SYSTEM_LIB_PREFIXES = (
    "linux-vdso.so",
    "ld-linux",
    "ld-musl",
    "libc.so",
    "libm.so",
    "libdl.so",
    "libpthread.so",
    "librt.so",
    "libresolv.so",
    "libutil.so",
    "libnsl.so",
    "libgcc_s.so",
    "libstdc++.so",
    "libpython",
)

WINDOWS_SYSTEM_DLL_PREFIXES = (
    "kernel32.dll",
    "user32.dll",
    "advapi32.dll",
    "ws2_32.dll",
    "iphlpapi.dll",
    "crypt32.dll",
    "bcrypt.dll",
    "secur32.dll",
    "shell32.dll",
    "ole32.dll",
    "ucrtbase.dll",
    "vcruntime",
    "msvcp",
    "api-ms-win-",
    "python3",
    "node.exe",
)


def _macos_list_deps(binary: Path) -> list[str]:
    res = subprocess.run(
        ["otool", "-L", str(binary)],
        capture_output=True,
        text=True,
        check=True,
    )
    deps: list[str] = []
    lines = res.stdout.splitlines()
    for idx, line in enumerate(lines):
        if idx == 0:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        dep_path = stripped.split(" (", 1)[0].strip()
        deps.append(dep_path)
    return deps


def _macos_is_external_dep(dep: str, own_path: Path) -> bool:
    if (
        dep == str(own_path)
        or Path(dep).name == own_path.name
        and not dep.startswith("/")
    ):
        return False
    if dep.startswith(("@loader_path", "@executable_path", "@rpath/Python")):
        return False
    if dep.startswith(MACOS_SYSTEM_PREFIXES):
        return False
    return dep.startswith("/") or dep.startswith("@rpath/")


def _macos_resolve_dep(dep: str, search_dirs: list[Path]) -> Path | None:
    if dep.startswith("/"):
        p = Path(dep)
        if p.is_file():
            return p.resolve()
    name = Path(dep).name
    for d in search_dirs:
        cand = d / name
        if cand.is_file():
            return cand.resolve()
    return None


def _codesign_adhoc(target: Path) -> None:
    codesign_bin = shutil.which("codesign")
    if codesign_bin:
        subprocess.run(
            [codesign_bin, "--force", "--sign", "-", str(target)],
            capture_output=True,
            text=True,
            check=False,
        )


def _bundle_macos(
    artifact: Path,
    libs_dir: Path,
    search_dirs: list[Path],
) -> list[str]:
    libs_dir.mkdir(parents=True, exist_ok=True)
    rel_libs = os.path.relpath(libs_dir, artifact.parent)
    loader_prefix = "@loader_path" if rel_libs == "." else f"@loader_path/{rel_libs}"

    copied_map: dict[str, Path] = {}
    queue: list[Path] = [artifact]
    visited: set[Path] = set()

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)

        for dep in _macos_list_deps(current):
            if not _macos_is_external_dep(dep, current):
                continue
            resolved = _macos_resolve_dep(dep, search_dirs)
            if resolved is None:
                continue
            dest_name = Path(dep).name
            dest_path = libs_dir / dest_name
            if not dest_path.exists():
                shutil.copy2(resolved, dest_path)
                dest_path.chmod(dest_path.stat().st_mode | stat.S_IWUSR | stat.S_IXUSR)
                queue.append(dest_path)
            copied_map[dep] = dest_path

    for bundled_lib in sorted(libs_dir.glob("*.dylib")):
        bundled_lib.chmod(bundled_lib.stat().st_mode | stat.S_IWUSR)
        subprocess.run(
            [
                "install_name_tool",
                "-id",
                f"@loader_path/{bundled_lib.name}",
                str(bundled_lib),
            ],
            check=True,
        )
        for dep in _macos_list_deps(bundled_lib):
            cand = libs_dir / Path(dep).name
            if _macos_is_external_dep(dep, bundled_lib) and cand.is_file():
                subprocess.run(
                    [
                        "install_name_tool",
                        "-change",
                        dep,
                        f"@loader_path/{cand.name}",
                        str(bundled_lib),
                    ],
                    check=True,
                )
        _codesign_adhoc(bundled_lib)

    artifact.chmod(artifact.stat().st_mode | stat.S_IWUSR)
    for dep in _macos_list_deps(artifact):
        cand = libs_dir / Path(dep).name
        if _macos_is_external_dep(dep, artifact) and cand.is_file():
            subprocess.run(
                [
                    "install_name_tool",
                    "-change",
                    dep,
                    f"{loader_prefix}/{cand.name}",
                    str(artifact),
                ],
                check=True,
            )
    _codesign_adhoc(artifact)

    return sorted(p.name for p in libs_dir.glob("*.dylib"))


def _linux_list_deps(binary: Path, clean_env: bool = False) -> list[tuple[str, str]]:
    env = dict(os.environ)
    if clean_env:
        env.pop("LD_LIBRARY_PATH", None)
    res = subprocess.run(
        ["ldd", str(binary)], capture_output=True, text=True, check=True, env=env
    )
    pairs: list[tuple[str, str]] = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if "=>" in line:
            left, right = line.split("=>", 1)
            soname = left.strip()
            resolved = right.strip().split(" (", 1)[0].strip()
            pairs.append((soname, resolved))
    return pairs


def _linux_is_system_lib(soname: str) -> bool:
    return any(soname.startswith(p) for p in LINUX_SYSTEM_LIB_PREFIXES)


def _bundle_linux(artifact: Path, libs_dir: Path) -> list[str]:
    libs_dir.mkdir(parents=True, exist_ok=True)
    rel_libs = os.path.relpath(libs_dir, artifact.parent)
    rpath_expr = "$ORIGIN" if rel_libs == "." else f"$ORIGIN/{rel_libs}"

    for soname, resolved in _linux_list_deps(artifact):
        if _linux_is_system_lib(soname) or not resolved or resolved == "not found":
            continue
        src = Path(resolved)
        if src.is_file():
            dest = libs_dir / soname
            if not dest.exists():
                shutil.copy2(src.resolve(), dest)
                dest.chmod(0o755)

    patchelf_bin = shutil.which("patchelf")
    if patchelf_bin:
        for bundled in sorted(libs_dir.glob("*.so*")):
            subprocess.run(
                [patchelf_bin, "--set-rpath", "$ORIGIN", str(bundled)], check=True
            )
        subprocess.run(
            [patchelf_bin, "--set-rpath", rpath_expr, str(artifact)], check=True
        )

    return sorted(p.name for p in libs_dir.glob("*.so*"))


def _pe_extract_dll_imports(binary: Path) -> list[str]:
    data = binary.read_bytes()
    valid_chars = set(
        b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"
    )
    matches: set[str] = set()
    offset = 0
    lower_data = data.lower()
    needle = b".dll"
    while True:
        idx = lower_data.find(needle, offset)
        if idx == -1:
            break
        start = idx
        while start > 0 and data[start - 1] in valid_chars:
            start -= 1
        raw_name = data[start : idx + 4]
        if len(raw_name) > 4:
            name = raw_name.decode("ascii", errors="ignore")
            matches.add(name)
        offset = idx + 4

    names = []
    for name in sorted(matches):
        low = name.lower()
        if low == binary.name.lower():
            continue
        if any(low.startswith(prefix) for prefix in WINDOWS_SYSTEM_DLL_PREFIXES):
            continue
        names.append(name)
    return names


def _bundle_windows(
    artifact: Path, libs_dir: Path, search_dirs: list[Path]
) -> list[str]:
    libs_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for dll_name in _pe_extract_dll_imports(artifact):
        for sdir in search_dirs:
            cand = sdir / dll_name
            if cand.is_file():
                dest = libs_dir / cand.name
                if not dest.exists():
                    shutil.copy2(cand, dest)
                copied.append(dest.name)
                break
    return sorted(set(copied))


def verify_self_contained(
    artifact: Path, libs_dir: Path | None = None
) -> dict[str, object]:
    """Verify that artifact and all bundled runtime libraries have zero external non-OS deps."""
    targets = [artifact]
    if libs_dir and libs_dir.is_dir():
        for p in sorted(libs_dir.iterdir()):
            if p.is_file() and (
                p.suffix in (".dylib", ".dll", ".so") or ".so." in p.name
            ):
                targets.append(p)

    external: list[dict[str, str]] = []
    inspected: dict[str, list[str]] = {}

    if sys.platform == "darwin":
        for t in targets:
            deps = _macos_list_deps(t)
            inspected[t.name] = deps
            for dep in deps:
                if _macos_is_external_dep(dep, t):
                    external.append({"binary": t.name, "dependency": dep})
    elif sys.platform.startswith("linux"):
        for t in targets:
            deps_pairs = _linux_list_deps(t, clean_env=True)
            inspected[t.name] = [f"{k} => {v}" for k, v in deps_pairs]
            for soname, resolved in deps_pairs:
                if _linux_is_system_lib(soname):
                    continue
                if resolved == "not found":
                    external.append({"binary": t.name, "dependency": soname})
                elif libs_dir and not str(Path(resolved).resolve()).startswith(
                    str(libs_dir.resolve())
                ):
                    external.append({"binary": t.name, "dependency": resolved})
    else:
        for t in targets:
            dlls = _pe_extract_dll_imports(t)
            inspected[t.name] = dlls

    return {
        "ok": len(external) == 0,
        "artifact": str(artifact),
        "libs_dir": str(libs_dir) if libs_dir else "",
        "external_dependencies": external,
        "inspected": inspected,
    }


def bundle_artifact(
    artifact: Path,
    libs_dir: Path | None = None,
    extra_search_dirs: list[Path] | None = None,
) -> dict[str, object]:
    """Bundle non-OS native libraries for artifact and verify self-containment."""
    artifact = artifact.resolve()
    if not artifact.is_file():
        raise FileNotFoundError(f"Native artifact not found: {artifact}")

    if libs_dir is None:
        if sys.platform == "darwin":
            libs_dir = artifact.parent / ".dylibs"
        elif sys.platform.startswith("linux"):
            libs_dir = artifact.parent / "libs"
        else:
            libs_dir = artifact.parent
    libs_dir = libs_dir.resolve()

    search_dirs: list[Path] = list(extra_search_dirs or [])
    for env_key in (
        "PURPLEAIR_CURL_BIN_DIR",
        "DYLD_LIBRARY_PATH",
        "LD_LIBRARY_PATH",
    ):
        raw = os.environ.get(env_key, "")
        for part in raw.split(os.pathsep):
            if part and Path(part).is_dir():
                search_dirs.append(Path(part).resolve())
    for std_dir in (
        Path("/opt/homebrew/lib"),
        Path("/opt/homebrew/opt/curl/lib"),
        Path("/opt/homebrew/opt/openssl@3/lib"),
        Path("/usr/local/lib"),
    ):
        if std_dir.is_dir():
            search_dirs.append(std_dir)

    if sys.platform == "darwin":
        bundled = _bundle_macos(artifact, libs_dir, search_dirs)
    elif sys.platform.startswith("linux"):
        bundled = _bundle_linux(artifact, libs_dir)
    else:
        bundled = _bundle_windows(artifact, libs_dir, search_dirs)

    report = verify_self_contained(artifact, libs_dir)
    report["bundled_libraries"] = bundled
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bundle and verify self-contained native libraries for SWIG packages."
    )
    parser.add_argument(
        "artifact", help="Path to compiled native binary (.so/.dylib/.dll/.node)"
    )
    parser.add_argument(
        "--libs-dir", default="", help="Directory to store bundled shared libs"
    )
    parser.add_argument(
        "--search-dir",
        action="append",
        default=[],
        help="Additional directory to search for runtime libraries",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify self-containment without modifying files",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args(argv)

    artifact = Path(args.artifact).resolve()
    libs_dir = Path(args.libs_dir).resolve() if args.libs_dir else None
    extra_dirs = [Path(p).resolve() for p in args.search_dir]

    if args.verify_only:
        report = verify_self_contained(artifact, libs_dir)
    else:
        report = bundle_artifact(
            artifact, libs_dir=libs_dir, extra_search_dirs=extra_dirs
        )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "SELF-CONTAINED" if report["ok"] else "EXTERNAL-DEPS-FOUND"
        print(f"[{status}] {artifact}")
        for b in report.get("bundled_libraries", []):
            print(f"  bundled: {b}")
        for ext in report.get("external_dependencies", []):
            print(
                f"  EXTERNAL: {ext['binary']} -> {ext['dependency']}", file=sys.stderr
            )

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
