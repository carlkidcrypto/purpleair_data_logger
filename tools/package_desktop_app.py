#!/usr/bin/env python3
"""Package PurpleAir Data Logger into standalone desktop applications.

Generates:
- Linux: Standalone executable (`PurpleAirDataLogger-Linux-<arch>`),
  Debian package (`PurpleAirDataLogger-Linux-<arch>.deb`),
  RPM package (`PurpleAirDataLogger-Linux-<arch>.rpm`),
  and portable `.tar.gz` archive.
- macOS: Standalone `.app` bundle (`PurpleAirDataLogger.app`),
  drag-and-drop disk image (`PurpleAirDataLogger-macOS-<arch>.dmg`),
  and `.zip` archive.
- Windows: Standalone single-file executable (`PurpleAirDataLogger-Windows-x64.exe`),
  Inno Setup installer (`PurpleAirDataLogger-Windows-x64-Setup.exe`),
  and portable `.zip` archives.
"""

from __future__ import annotations

import argparse
import io
import os
import platform
import plistlib
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def read_version() -> str:
    """Read the current project CalSemVer string from src/version.cpp or fallback."""
    version_file = REPO_ROOT / "src" / "version.cpp"
    if version_file.is_file():
        text = version_file.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "PROJECT_VERSION_STRING" in line and '"' in line:
                return line.split('"')[1].strip()
    return "2026.11.3a0"


def resolve_platform(requested: str) -> str:
    """Resolve target platform string to 'windows', 'macos', or 'linux'."""
    val = (requested or "auto").strip().lower()
    if val in ("windows", "win", "win32"):
        return "windows"
    if val in ("macos", "darwin", "osx", "apple"):
        return "macos"
    if val in ("linux", "posix"):
        return "linux"

    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def build_pyinstaller_cmd(
    target_os: str,
    version: str,
    dist_dir: Path,
    build_dir: Path,
) -> list[str]:
    """Assemble the PyInstaller command invocation with all required flags and assets."""
    entry_script = REPO_ROOT / "purpleair_data_logger" / "entry_desktop.py"
    if not entry_script.is_file():
        raise FileNotFoundError(f"Missing desktop entry point: {entry_script}")

    sep = ";" if target_os == "windows" else ":"

    cmd: list[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(build_dir),
        "--specpath",
        str(build_dir),
    ]

    static_dir = REPO_ROOT / "purpleair_data_logger" / "gui" / "static"
    if static_dir.is_dir():
        cmd.extend(["--add-data", f"{static_dir}{sep}purpleair_data_logger/gui/static"])

    locale_file = REPO_ROOT / "purpleair_data_logger" / "gui" / "locale.json"
    if locale_file.is_file():
        cmd.extend(["--add-data", f"{locale_file}{sep}purpleair_data_logger/gui"])

    config_example = REPO_ROOT / "configs" / "example.json"
    if config_example.is_file():
        cmd.extend(["--add-data", f"{config_example}{sep}configs"])

    hidden_imports = [
        "purpleair_api",
        "purpleair_data_logger",
        "purpleair_data_logger.purpleair_data_logger_swig",
        "purpleair_data_logger.cli",
        "purpleair_data_logger.gui",
        "purpleair_data_logger.gui.desktop_tk",
        "purpleair_data_logger.gui.server",
        "purpleair_data_logger.gui.cli_bridge",
        "purpleair_data_logger.gui.launcher",
        "purpleair_data_logger.gui.locale_manager",
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "sqlite3",
        "json",
        "http.server",
        "webbrowser",
        "urllib.request",
        "multiprocessing",
    ]
    for mod in hidden_imports:
        cmd.extend(["--hidden-import", mod])

    if target_os == "macos":
        icon_icns = static_dir / "app_icon.icns"
        if icon_icns.is_file():
            cmd.extend(["--icon", str(icon_icns)])

        dylibs_dir = REPO_ROOT / "purpleair_data_logger" / ".dylibs"
        if dylibs_dir.is_dir():
            for dylib in dylibs_dir.glob("*.dylib"):
                cmd.extend(
                    ["--add-binary", f"{dylib}{sep}purpleair_data_logger/.dylibs"]
                )

        for so_file in (REPO_ROOT / "purpleair_data_logger").glob(
            "_purpleair_data_logger*.so"
        ):
            cmd.extend(["--add-binary", f"{so_file}{sep}purpleair_data_logger"])

        cmd.extend(
            [
                "--onedir",
                "--windowed",
                "--name",
                "PurpleAirDataLogger",
                "--osx-bundle-identifier",
                "com.carlkidcrypto.purpleair-data-logger",
            ]
        )

    elif target_os == "windows":
        icon_ico = static_dir / "app_icon.ico"
        if icon_ico.is_file():
            cmd.extend(["--icon", str(icon_ico)])

        for dll_file in (REPO_ROOT / "purpleair_data_logger").glob("*.dll"):
            cmd.extend(["--add-binary", f"{dll_file}{sep}purpleair_data_logger"])

        for pyd_file in (REPO_ROOT / "purpleair_data_logger").glob(
            "_purpleair_data_logger*.pyd"
        ):
            cmd.extend(["--add-binary", f"{pyd_file}{sep}purpleair_data_logger"])

        cmd.extend(
            [
                "--onefile",
                "--name",
                "PurpleAirDataLogger",
            ]
        )

    else:
        icon_png = static_dir / "app_icon.png"
        if icon_png.is_file():
            cmd.extend(["--icon", str(icon_png)])

        for so_file in (REPO_ROOT / "purpleair_data_logger").glob(
            "_purpleair_data_logger*.so"
        ):
            cmd.extend(["--add-binary", f"{so_file}{sep}purpleair_data_logger"])

        cmd.extend(
            [
                "--onefile",
                "--name",
                "PurpleAirDataLogger",
            ]
        )

    cmd.append(str(entry_script))
    return cmd


def package_macos_dmg(
    dist_dir: Path,
    version: str,
    arch: str,
) -> Path:
    """Wrap PurpleAirDataLogger.app into a compressed DMG with an Applications symlink."""
    app_path = dist_dir / "PurpleAirDataLogger.app"
    if not app_path.is_dir():
        raise FileNotFoundError(f"Expected macOS app bundle not found at: {app_path}")

    plist_path = app_path / "Contents" / "Info.plist"
    if plist_path.is_file():
        try:
            with open(plist_path, "rb") as f:
                data = plistlib.load(f)
            data["CFBundleName"] = "PurpleAirDataLogger"
            data["CFBundleDisplayName"] = "PurpleAir Data Logger"
            data["CFBundleExecutable"] = "PurpleAirDataLogger"
            data["CFBundleIdentifier"] = "com.carlkidcrypto.purpleair-data-logger"
            data["CFBundleShortVersionString"] = version
            data["CFBundleVersion"] = version
            data["NSHighResolutionCapable"] = True
            data["LSMinimumSystemVersion"] = "11.0"
            with open(plist_path, "wb") as f:
                plistlib.dump(data, f)
        except Exception as exc:
            print(f"Warning: Could not update Info.plist: {exc}")

    codesign = shutil.which("codesign")
    if codesign:
        subprocess.run(
            [codesign, "--force", "--deep", "--sign", "-", str(app_path)],
            check=False,
            capture_output=True,
        )

    zip_out = dist_dir / f"PurpleAirDataLogger-macOS-{arch}.zip"
    print(f"Creating macOS ZIP archive: {zip_out} ...")
    subprocess.run(
        ["zip", "-r", "-y", str(zip_out), app_path.name],
        cwd=dist_dir,
        check=True,
    )

    staging_dir = dist_dir / "dmg_staging"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    target_app = staging_dir / app_path.name
    shutil.copytree(app_path, target_app, symlinks=True)

    apps_link = staging_dir / "Applications"
    if not apps_link.exists():
        os.symlink("/Applications", str(apps_link))

    dmg_out = dist_dir / f"PurpleAirDataLogger-macOS-{arch}.dmg"
    if dmg_out.is_file():
        dmg_out.unlink()

    subprocess.run(
        [
            "hdiutil",
            "create",
            "-volname",
            "PurpleAirDataLogger",
            "-srcfolder",
            str(staging_dir),
            "-ov",
            "-format",
            "UDZO",
            str(dmg_out),
        ],
        check=True,
    )

    shutil.rmtree(staging_dir, ignore_errors=True)
    return dmg_out


def find_iscc_compiler() -> str | None:
    """Locate the Inno Setup ISCC.exe compiler on Windows."""
    which_iscc = shutil.which("iscc")
    if which_iscc:
        return which_iscc

    standard_paths = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"),
    ]
    for p in standard_paths:
        if p.is_file():
            return str(p)
    return None


def package_windows_artifacts(
    dist_dir: Path,
    version: str,
    arch: str,
    skip_installer: bool = False,
) -> list[Path]:
    """Generate standalone Windows executable copies, ZIP archives, and Inno Setup installer."""
    exe_src = dist_dir / "PurpleAirDataLogger.exe"
    if not exe_src.is_file():
        raise FileNotFoundError(f"Expected Windows executable not found at: {exe_src}")

    arch_exe = dist_dir / f"PurpleAirDataLogger-Windows-{arch}.exe"
    shutil.copy2(exe_src, arch_exe)
    results = [arch_exe]

    zip_paths = [
        dist_dir / f"purpleair_data_logger-windows-{arch.lower()}.zip",
        dist_dir / f"PurpleAirDataLogger-Windows-{arch}.zip",
    ]
    for zpath in zip_paths:
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(exe_src, arcname="PurpleAirDataLogger.exe")
            zf.write(exe_src, arcname="purpleair-data-logger.exe")
            ico = (
                REPO_ROOT / "purpleair_data_logger" / "gui" / "static" / "app_icon.ico"
            )
            if ico.is_file():
                zf.write(ico, arcname="app_icon.ico")
            license_file = REPO_ROOT / "LICENSE"
            if license_file.is_file():
                zf.write(license_file, arcname="LICENSE")
            readme_file = REPO_ROOT / "README.md"
            if readme_file.is_file():
                zf.write(readme_file, arcname="README.md")
        results.append(zpath)

    if not skip_installer:
        iscc = find_iscc_compiler()
        iss_file = REPO_ROOT / "tools" / "windows_installer.iss"
        if iscc and iss_file.is_file():
            cmd = [
                iscc,
                f"/DAppVersion={version}",
                f"/DSourceExe={exe_src.resolve()}",
                str(iss_file.resolve()),
            ]
            subprocess.run(cmd, check=True)
            setup_exe = dist_dir / "PurpleAirDataLogger-Windows-x64-Setup.exe"
            if setup_exe.is_file():
                results.append(setup_exe)

    return results


def build_deb_package(
    staging_dir: Path,
    output_deb_path: Path,
) -> Path:
    """Build a Debian .deb package using dpkg-deb if available, or pure Python fallback."""
    dpkg_deb = shutil.which("dpkg-deb")
    if dpkg_deb:
        subprocess.run(
            [
                dpkg_deb,
                "-Zgzip",
                "--build",
                "--root-owner-group",
                str(staging_dir),
                str(output_deb_path),
            ],
            check=True,
        )
        return output_deb_path

    debian_binary = b"2.0\n"

    control_buf = io.BytesIO()
    with tarfile.open(fileobj=control_buf, mode="w:gz") as tar:
        for p in sorted((staging_dir / "DEBIAN").rglob("*")):
            if p.is_file():
                rel = p.relative_to(staging_dir / "DEBIAN")
                tar.add(p, arcname=f"./{rel}")
    control_data = control_buf.getvalue()

    data_buf = io.BytesIO()
    with tarfile.open(fileobj=data_buf, mode="w:gz") as tar:
        for p in sorted(staging_dir.rglob("*")):
            if p.name == "DEBIAN" or "DEBIAN" in p.parts:
                continue
            rel = p.relative_to(staging_dir)
            tar.add(p, arcname=f"./{rel}")
    data_data = data_buf.getvalue()

    with open(output_deb_path, "wb") as f:
        f.write(b"!<arch>\n")
        for name, chunk in [
            ("debian-binary", debian_binary),
            ("control.tar.gz", control_data),
            ("data.tar.gz", data_data),
        ]:
            mtime = int(time.time())
            hdr = f"{name:<16}{mtime:<12}0     0     100644  {len(chunk):<10}`\n"
            f.write(hdr.encode("ascii"))
            f.write(chunk)
            if len(chunk) % 2 != 0:
                f.write(b"\n")

    return output_deb_path


def package_linux_artifacts(
    dist_dir: Path,
    version: str,
    arch: str,
    skip_deb: bool = False,
    skip_rpm: bool = False,
) -> list[Path]:
    """Generate standalone Linux executable copies, tarball, Debian (.deb) and RPM (.rpm) packages."""
    exe_src = dist_dir / "PurpleAirDataLogger"
    if not exe_src.is_file():
        raise FileNotFoundError(f"Expected Linux executable not found at: {exe_src}")

    arch_exe = dist_dir / f"PurpleAirDataLogger-Linux-{arch}"
    shutil.copy2(exe_src, arch_exe)
    arch_exe.chmod(0o755)
    results = [arch_exe]

    desktop_file = dist_dir / "purpleair-data-logger.desktop"
    desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=PurpleAir Data Logger
GenericName=Air Quality Data Logger
Comment=Cross-Platform PurpleAir Telemetry Engine and Data Logger
Exec=PurpleAirDataLogger %F
Icon=purpleair-data-logger
Terminal=false
Categories=Science;Network;Development;System;Utility;
Keywords=purpleair;air-quality;telemetry;data-logger;sensors;monitoring;
StartupNotify=true
StartupWMClass=PurpleAirDataLogger
"""
    desktop_file.write_text(desktop_content, encoding="utf-8")
    desktop_file.chmod(0o644)

    icon_src = REPO_ROOT / "purpleair_data_logger" / "gui" / "static" / "app_icon.png"
    license_src = REPO_ROOT / "LICENSE"
    readme_src = REPO_ROOT / "README.md"

    tar_path = dist_dir / f"PurpleAirDataLogger-Linux-{arch}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(exe_src, arcname="PurpleAirDataLogger")
        tar.add(desktop_file, arcname="purpleair-data-logger.desktop")
        if icon_src.is_file():
            tar.add(icon_src, arcname="purpleair-data-logger.png")
        if license_src.is_file():
            tar.add(license_src, arcname="LICENSE")
        if readme_src.is_file():
            tar.add(readme_src, arcname="README.md")
    results.append(tar_path)

    deb_arch = "amd64" if arch in ("x64", "x86_64") else arch
    rpm_arch = "x86_64" if arch in ("x64", "amd64") else arch
    clean_version = version.replace("-", ".")

    if not skip_deb:
        deb_out = dist_dir / f"PurpleAirDataLogger-Linux-{arch}.deb"
        deb_canonical = dist_dir / f"purpleair-data-logger_{version}_{deb_arch}.deb"
        staging = dist_dir / "deb_staging"
        if staging.exists():
            shutil.rmtree(staging)

        (staging / "DEBIAN").mkdir(parents=True, exist_ok=True)
        (staging / "usr" / "bin").mkdir(parents=True, exist_ok=True)
        (staging / "usr" / "share" / "applications").mkdir(parents=True, exist_ok=True)
        (staging / "usr" / "share" / "pixmaps").mkdir(parents=True, exist_ok=True)
        (staging / "usr" / "share" / "doc" / "PurpleAirDataLogger").mkdir(
            parents=True, exist_ok=True
        )

        control_content = f"""Package: purpleair-data-logger
Version: {version}
Section: utils
Priority: optional
Architecture: {deb_arch}
Maintainer: Carlos Santos <carlkidcrypto@users.noreply.github.com>
Installed-Size: {int(exe_src.stat().st_size / 1024)}
Description: PurpleAir Data Logger
 Self-contained C++17 PurpleAir telemetry engine and data logger with SWIG
 bindings, CLI, and GUI Studio.
Homepage: https://carlkidcrypto.github.io/purpleair_data_logger/
"""
        (staging / "DEBIAN" / "control").write_text(control_content, encoding="utf-8")
        shutil.copy2(exe_src, staging / "usr" / "bin" / "PurpleAirDataLogger")
        (staging / "usr" / "bin" / "PurpleAirDataLogger").chmod(0o755)
        os.symlink(
            "PurpleAirDataLogger",
            str(staging / "usr" / "bin" / "purpleair-data-logger"),
        )

        shutil.copy2(
            desktop_file,
            staging
            / "usr"
            / "share"
            / "applications"
            / "purpleair-data-logger.desktop",
        )
        if icon_src.is_file():
            shutil.copy2(
                icon_src,
                staging / "usr" / "share" / "pixmaps" / "purpleair-data-logger.png",
            )
        if license_src.is_file():
            shutil.copy2(
                license_src,
                staging / "usr" / "share" / "doc" / "PurpleAirDataLogger" / "copyright",
            )
        if readme_src.is_file():
            shutil.copy2(
                readme_src,
                staging / "usr" / "share" / "doc" / "PurpleAirDataLogger" / "README.md",
            )

        build_deb_package(staging, deb_out)
        shutil.copy2(deb_out, deb_canonical)
        results.extend([deb_out, deb_canonical])
        shutil.rmtree(staging, ignore_errors=True)

    if not skip_rpm:
        rpm_out = dist_dir / f"PurpleAirDataLogger-Linux-{arch}.rpm"
        rpm_canonical = (
            dist_dir / f"purpleair-data-logger-{clean_version}-1.{rpm_arch}.rpm"
        )
        rpmbuild = shutil.which("rpmbuild")
        if rpmbuild:
            rpm_top = dist_dir / "rpmbuild"
            if rpm_top.exists():
                shutil.rmtree(rpm_top)
            for d in ["BUILD", "BUILDROOT", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
                (rpm_top / d).mkdir(parents=True, exist_ok=True)

            shutil.copy2(exe_src, rpm_top / "SOURCES" / "PurpleAirDataLogger")
            shutil.copy2(
                desktop_file, rpm_top / "SOURCES" / "purpleair-data-logger.desktop"
            )
            if icon_src.is_file():
                shutil.copy2(
                    icon_src, rpm_top / "SOURCES" / "purpleair-data-logger.png"
                )
            if license_src.is_file():
                shutil.copy2(license_src, rpm_top / "SOURCES" / "LICENSE")

            spec_content = f"""Name:           PurpleAirDataLogger
Version:        {clean_version}
Release:        1
Summary:        Self-contained C++17 PurpleAir Telemetry Engine and Data Logger
License:        MIT
URL:            https://carlkidcrypto.github.io/purpleair_data_logger/
Group:          Applications/System
AutoReqProv:    no

%description
PurpleAir Data Logger provides high-performance PurpleAir air-quality telemetry
ingestion, local storage sinks (SQLite3, JSONL, CSV, Prometheus, PostgreSQL),
and unified CLI/GUI operation across Windows, Linux, and macOS.

%install
rm -rf %{{buildroot}}
mkdir -p %{{buildroot}}/usr/bin
mkdir -p %{{buildroot}}/usr/share/applications
mkdir -p %{{buildroot}}/usr/share/pixmaps
mkdir -p %{{buildroot}}/usr/share/doc/PurpleAirDataLogger

install -m 755 %{{_sourcedir}}/PurpleAirDataLogger %{{buildroot}}/usr/bin/PurpleAirDataLogger
ln -sf PurpleAirDataLogger %{{buildroot}}/usr/bin/purpleair-data-logger
install -m 644 %{{_sourcedir}}/purpleair-data-logger.desktop %{{buildroot}}/usr/share/applications/purpleair-data-logger.desktop
if [ -f "%{{_sourcedir}}/purpleair-data-logger.png" ]; then
  install -m 644 %{{_sourcedir}}/purpleair-data-logger.png %{{buildroot}}/usr/share/pixmaps/purpleair-data-logger.png
fi
if [ -f "%{{_sourcedir}}/LICENSE" ]; then
  install -m 644 %{{_sourcedir}}/LICENSE %{{buildroot}}/usr/share/doc/PurpleAirDataLogger/LICENSE
fi

%files
/usr/bin/PurpleAirDataLogger
/usr/bin/purpleair-data-logger
/usr/share/applications/purpleair-data-logger.desktop
%ghost /usr/share/pixmaps/purpleair-data-logger.png
%ghost /usr/share/doc/PurpleAirDataLogger/LICENSE
"""
            spec_file = rpm_top / "SPECS" / "PurpleAirDataLogger.spec"
            spec_file.write_text(spec_content, encoding="utf-8")
            cmd = [
                rpmbuild,
                "-bb",
                "--define",
                f"_topdir {rpm_top.resolve()}",
                "--target",
                rpm_arch,
                str(spec_file.resolve()),
            ]
            subprocess.run(cmd, check=True)
            built_rpms = list((rpm_top / "RPMS").rglob("*.rpm"))
            if built_rpms:
                shutil.copy2(built_rpms[0], rpm_out)
                shutil.copy2(built_rpms[0], rpm_canonical)
                results.extend([rpm_out, rpm_canonical])
            shutil.rmtree(rpm_top, ignore_errors=True)

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Package PurpleAir Data Logger for desktop distribution."
    )
    parser.add_argument(
        "--platform",
        choices=["auto", "windows", "macos", "linux"],
        default="auto",
        help="Target platform to package (defaults to current OS).",
    )
    parser.add_argument(
        "--version",
        default="",
        help="Override version string (defaults to src/version.cpp).",
    )
    parser.add_argument(
        "--dist-dir",
        type=Path,
        default=REPO_ROOT / "dist",
        help="Target output directory for distributions.",
    )
    parser.add_argument(
        "--skip-dmg",
        action="store_true",
        help="Skip macOS DMG creation.",
    )
    parser.add_argument(
        "--skip-installer",
        action="store_true",
        help="Skip Windows Inno Setup installer compilation.",
    )
    parser.add_argument(
        "--skip-deb",
        action="store_true",
        help="Skip Linux Debian .deb package creation.",
    )
    parser.add_argument(
        "--skip-rpm",
        action="store_true",
        help="Skip Linux Red Hat .rpm package creation.",
    )
    args = parser.parse_args(argv)

    target_os = resolve_platform(args.platform)
    ver = args.version or read_version()
    dist_dir = args.dist_dir.resolve()
    build_dir = REPO_ROOT / "build_pyinstaller"

    dist_dir.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    cmd = build_pyinstaller_cmd(target_os, ver, dist_dir, build_dir)
    subprocess.run(cmd, check=True)

    arch = platform.machine().lower()
    if arch in ("x86_64", "amd64"):
        arch = "x64"

    if target_os == "macos" and not args.skip_dmg:
        package_macos_dmg(dist_dir, ver, arch)
    elif target_os == "windows":
        package_windows_artifacts(
            dist_dir, ver, arch, skip_installer=args.skip_installer
        )
    elif target_os == "linux":
        package_linux_artifacts(
            dist_dir, ver, arch, skip_deb=args.skip_deb, skip_rpm=args.skip_rpm
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
