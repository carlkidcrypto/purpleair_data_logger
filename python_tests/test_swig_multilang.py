"""Verify 4-language SWIG codegen (python, javascript, csharp, go) and JSON config templates."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import purpleair_data_logger as pdl
from tools.generate_swig_bindings import SWIG_LANGUAGE_TARGETS, generate_for_language
from tools.generate_winget_manifest import generate_manifests

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_all_repository_json_configs_are_valid() -> None:
    cfg_dir = REPO_ROOT / "configs"
    json_files = sorted(cfg_dir.glob("*.json"))
    assert len(json_files) >= 4
    for jf in json_files:
        rep = pdl.validate_config_file(str(jf))
        assert rep.valid is True, f"{jf.name} failed validation: {list(rep.errors)}"


def test_supported_swig_targets_match_bindings_scaffolds() -> None:
    assert list(SWIG_LANGUAGE_TARGETS.keys()) == [
        "python",
        "javascript",
        "csharp",
        "go",
    ]
    bindings_dirs = sorted(
        p.name for p in (REPO_ROOT / "bindings").iterdir() if p.is_dir()
    )
    assert bindings_dirs == ["csharp", "go", "javascript"]


@pytest.mark.skipif(
    shutil.which("swig") is None, reason="SWIG CLI not installed on PATH"
)
def test_swig_generates_wrappers_for_all_4_targets(tmp_path: Path) -> None:
    swig_bin = shutil.which("swig")
    assert swig_bin is not None
    for lang in SWIG_LANGUAGE_TARGETS:
        res = generate_for_language(swig_bin, lang, tmp_path)
        assert res["ok"] is True, f"SWIG codegen failed for {lang}: {res['stderr']}"
        assert len(res["generated_files"]) >= 1


def test_winget_manifest_generation(tmp_path: Path) -> None:
    zip_manifests = generate_manifests(
        package_id="carlkidcrypto.PurpleAirDataLogger",
        package_version="2026.11.3",
        installer_url="https://github.com/carlkidcrypto/purpleair_data_logger/releases/download/v2026.11.3/PurpleAirDataLogger-Windows-x64.zip",
        installer_sha256="aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899",
        out_dir=tmp_path / "zip_out",
        architecture="x64",
        installer_type="zip",
    )
    assert set(zip_manifests.keys()) == {"version", "locale", "installer"}
    canonical_zip_dir = (
        tmp_path
        / "zip_out"
        / "manifests"
        / "c"
        / "carlkidcrypto"
        / "PurpleAirDataLogger"
        / "2026.11.3"
    )
    for p in zip_manifests.values():
        assert p.is_file()
        assert p.parent == canonical_zip_dir
        content = p.read_text(encoding="utf-8")
        assert "carlkidcrypto.PurpleAirDataLogger" in content
        assert "2026.11.3" in content

    zip_installer_content = zip_manifests["installer"].read_text(encoding="utf-8")
    assert "InstallerType: zip" in zip_installer_content
    assert "NestedInstallerType: portable" in zip_installer_content
    assert "RelativeFilePath: PurpleAirDataLogger.exe" in zip_installer_content
    assert "PortableCommandAlias: purpleair-data-logger" in zip_installer_content

    inno_manifests = generate_manifests(
        package_id="carlkidcrypto.PurpleAirDataLogger",
        package_version="2026.11.3",
        installer_url="https://github.com/carlkidcrypto/purpleair_data_logger/releases/download/v2026.11.3/PurpleAirDataLogger-Windows-x64-Setup.exe",
        installer_sha256="11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
        out_dir=tmp_path / "inno_out",
        architecture="x64",
        installer_type="inno",
    )
    canonical_inno_dir = (
        tmp_path
        / "inno_out"
        / "manifests"
        / "c"
        / "carlkidcrypto"
        / "PurpleAirDataLogger"
        / "2026.11.3"
    )
    for p in inno_manifests.values():
        assert p.is_file()
        assert p.parent == canonical_inno_dir

    inno_installer_content = inno_manifests["installer"].read_text(encoding="utf-8")
    assert "InstallerType: inno" in inno_installer_content
    assert "Scope: user" in inno_installer_content
    assert "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART" in inno_installer_content
    assert "AppsAndFeaturesEntries:" in inno_installer_content
    assert "{B7C9F812-3D4A-491B-8E72-554F912A6D3C}_is1" in inno_installer_content

    locale_content = inno_manifests["locale"].read_text(encoding="utf-8")
    assert "Moniker: purpleair-data-logger" in locale_content
    assert "License: MIT" in locale_content
    assert "Publisher: carlkidcrypto" in locale_content
