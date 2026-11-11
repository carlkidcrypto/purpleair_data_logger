"""Unit tests for standalone desktop application packaging (Windows EXE, macOS DMG, Linux DEB & RPM)."""

from __future__ import annotations

import sys
import tarfile
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from purpleair_data_logger.entry_desktop import main as entry_desktop_main
from tools.package_desktop_app import (
    build_pyinstaller_cmd,
    package_linux_artifacts,
    read_version,
)


def _flush_libc() -> None:
    try:
        import ctypes

        if sys.platform == "win32":
            for lib in ("ucrtbase", "msvcrt"):
                try:
                    ctypes.CDLL(lib).fflush(None)
                except Exception:
                    pass
        else:
            ctypes.CDLL(None).fflush(None)
    except Exception:
        pass
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except Exception:
        pass


def test_desktop_entry_dispatch_cli_subcommands(
    capfd: pytest.CaptureFixture[str],
) -> None:
    ret_version = entry_desktop_main(["version"])
    _flush_libc()
    captured_ver = capfd.readouterr()
    assert ret_version == 0
    assert "purpleair_data_logger" in captured_ver.out
    assert "2026.11" in captured_ver.out

    ret_cli_ver = entry_desktop_main(["cli", "version"])
    _flush_libc()
    captured_cli_ver = capfd.readouterr()
    assert ret_cli_ver == 0
    assert "purpleair_data_logger" in captured_cli_ver.out

    ret_help = entry_desktop_main(["help"])
    _flush_libc()
    captured_help = capfd.readouterr()
    assert ret_help == 0
    assert "Usage:" in captured_help.out


def test_desktop_entry_dispatches_gui_when_empty() -> None:
    with patch("purpleair_data_logger.gui.main", return_value=0) as mock_gui:
        ret = entry_desktop_main([])
        assert ret == 0
        mock_gui.assert_called_once_with([])


def test_package_desktop_pyinstaller_cmd_assembly() -> None:
    version = read_version()
    dist_dir = REPO_ROOT / "dist"
    build_dir = REPO_ROOT / "build_pyinstaller"

    cmd_macos = build_pyinstaller_cmd("macos", version, dist_dir, build_dir)
    cmd_macos_str = " ".join(cmd_macos)
    assert "--onedir" in cmd_macos
    assert "--windowed" in cmd_macos
    assert "PurpleAirDataLogger" in cmd_macos
    assert "com.carlkidcrypto.purpleair-data-logger" in cmd_macos
    assert "app_icon.icns" in cmd_macos_str
    assert "entry_desktop.py" in cmd_macos[-1]

    cmd_win = build_pyinstaller_cmd("windows", version, dist_dir, build_dir)
    cmd_win_str = " ".join(cmd_win)
    assert "--onefile" in cmd_win
    assert "PurpleAirDataLogger" in cmd_win
    assert "app_icon.ico" in cmd_win_str
    assert "entry_desktop.py" in cmd_win[-1]

    cmd_linux = build_pyinstaller_cmd("linux", version, dist_dir, build_dir)
    cmd_linux_str = " ".join(cmd_linux)
    assert "--onefile" in cmd_linux
    assert "PurpleAirDataLogger" in cmd_linux
    assert "app_icon.png" in cmd_linux_str
    assert "entry_desktop.py" in cmd_linux[-1]


def test_package_linux_artifacts_deb_and_tarball(tmp_path: Path) -> None:
    mock_bin = tmp_path / "PurpleAirDataLogger"
    mock_bin.write_text("#!/bin/sh\necho 'PurpleAirDataLogger'\n", encoding="utf-8")
    mock_bin.chmod(0o755)

    artifacts = package_linux_artifacts(
        dist_dir=tmp_path,
        version="2026.11.3",
        arch="x64",
        skip_deb=False,
        skip_rpm=True,
    )

    names = [a.name for a in artifacts]
    assert "PurpleAirDataLogger-Linux-x64" in names
    assert "PurpleAirDataLogger-Linux-x64.tar.gz" in names
    assert "PurpleAirDataLogger-Linux-x64.deb" in names
    assert "purpleair-data-logger_2026.11.3_amd64.deb" in names

    tar_path = tmp_path / "PurpleAirDataLogger-Linux-x64.tar.gz"
    with tarfile.open(tar_path, "r:gz") as tar:
        tar_names = tar.getnames()
        assert "PurpleAirDataLogger" in tar_names
        assert "purpleair-data-logger.desktop" in tar_names

    deb_path = tmp_path / "PurpleAirDataLogger-Linux-x64.deb"
    with open(deb_path, "rb") as f:
        magic = f.read(8)
        assert magic == b"!<arch>\n"
        rest = f.read()
        assert b"debian-binary" in rest
        assert b"control.tar" in rest
        assert b"data.tar" in rest


def test_inno_setup_script_structure() -> None:
    iss_file = REPO_ROOT / "tools" / "windows_installer.iss"
    assert iss_file.is_file(), "Missing tools/windows_installer.iss"

    content = iss_file.read_text(encoding="utf-8")
    assert "AppId={{B7C9F812-3D4A-491B-8E72-554F912A6D3C}" in content
    assert "AppName=PurpleAir Data Logger" in content
    assert "OutputBaseFilename=PurpleAirDataLogger-Windows-x64-Setup" in content
    assert "PurpleAirDataLogger.exe" in content
    assert "purpleair-data-logger.exe" in content
    assert "desktopicon" in content
    assert "envPath" in content
