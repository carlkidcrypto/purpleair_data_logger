"""Tests for the Python SWIG 4.x C++17 bindings and self-containment of purpleair_data_logger."""

from __future__ import annotations

import json
import re
import shutil
import sys
import tomllib
from pathlib import Path

import pytest

import purpleair_data_logger as pdl
from tools import bundle_native_package


def test_calsemver_version_and_capabilities() -> None:
    assert pdl.__version__ == "2026.11.3a0"
    assert pdl.version() == "2026.11.3a0"
    assert pdl.purpleair_api_target_version() == "2026.11.3"
    assert pdl.is_valid_calsemver(pdl.__version__) is True
    assert pdl.is_valid_calsemver(pdl.purpleair_api_target_version()) is True
    assert pdl.is_valid_calsemver("2026.11.1") is True
    assert pdl.is_valid_calsemver("v2026.11.9") is True
    assert pdl.is_valid_calsemver("2026.11.3-alpha.0") is True
    assert pdl.is_valid_calsemver("2026.01.05") is False
    assert pdl.is_valid_calsemver("0.1.0") is False
    assert pdl.has_sqlite3_support() is True
    assert pdl.has_embedded_sqlite3() is True
    assert isinstance(pdl.has_psql_support(), bool)
    assert pdl.has_native_engine() is True
    if sys.platform != "win32":
        assert pdl.has_purpleair_api_support() is True

    langs = list(pdl.supported_swig_languages())
    assert langs == ["python", "javascript", "csharp", "go"]

    info = pdl.build_info()
    assert "purpleair_data_logger 2026.11.3a0" in info
    assert "C++17" in info
    assert "sqlite3=enabled" in info


def test_all_project_manifests_synchronized_on_calsemver() -> None:
    """Verify every project manifest uses synchronized CalSemVer."""
    repo_root = Path(__file__).resolve().parent.parent
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.is_file():
        pytest.skip("Repository manifests unavailable outside source checkout")

    expected_pep440 = pdl.version()
    assert pdl.is_valid_calsemver(expected_pep440)
    m_base = re.match(
        r"^(\d{4}\.\d+\.\d+)(?:\.(\d+))?(?:a(\d+)|b(\d+)|rc(\d+))?$", expected_pep440
    )
    assert m_base is not None
    cal_core = m_base.group(1)
    if m_base.group(2) is not None:
        expected_semver = f"{cal_core}-{m_base.group(2)}"
        expected_csharp = expected_pep440
    elif m_base.group(3) is not None:
        expected_semver = f"{cal_core}-alpha.{m_base.group(3)}"
        expected_csharp = expected_semver
    elif m_base.group(4) is not None:
        expected_semver = f"{cal_core}-beta.{m_base.group(4)}"
        expected_csharp = expected_semver
    elif m_base.group(5) is not None:
        expected_semver = f"{cal_core}-rc.{m_base.group(5)}"
        expected_csharp = expected_semver
    else:
        expected_semver = cal_core
        expected_csharp = cal_core

    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    assert pyproject["project"]["version"] == expected_pep440

    meson_text = (repo_root / "meson.build").read_text(encoding="utf-8")
    assert f"version: '{expected_pep440}'" in meson_text

    cmake_text = (repo_root / "CMakeLists.txt").read_text(encoding="utf-8")
    assert f"VERSION {cal_core}" in cmake_text
    assert f'PURPLEAIR_DL_VERSION_STRING "{expected_pep440}"' in cmake_text

    npm_pkg = json.loads(
        (repo_root / "bindings" / "javascript" / "package.json").read_text(
            encoding="utf-8"
        )
    )
    assert npm_pkg["version"] == expected_semver
    assert pdl.is_valid_calsemver(npm_pkg["version"])

    csproj_text = (
        repo_root / "bindings" / "csharp" / "PurpleAirDataLogger.csproj"
    ).read_text(encoding="utf-8")
    assert f"<Version>{expected_csharp}</Version>" in csproj_text


def test_self_contained_native_extension_bundling(tmp_path: Path) -> None:
    """Verify zero external libsqlite3 dep & clean native bundling."""
    pkg_dir = Path(pdl.__file__).resolve().parent
    ext_candidates = list(pkg_dir.glob("_purpleair_data_logger*.so")) + list(
        pkg_dir.glob("_purpleair_data_logger*.pyd")
    )
    assert len(ext_candidates) >= 1
    src_ext = ext_candidates[0]

    staged_ext = tmp_path / src_ext.name
    shutil.copy2(src_ext, staged_ext)

    report = bundle_native_package.bundle_artifact(staged_ext)
    assert report["ok"] is True, f"External deps remained after bundling: {report}"
    assert report["external_dependencies"] == []

    bundled_names = [name.lower() for name in report.get("bundled_libraries", [])]
    assert not any("sqlite" in name for name in bundled_names)


def test_datatypes_and_purpleair_field_ingestion() -> None:
    s_pm = pdl.Sample.from_purpleair_field(
        "pm2_5_atm", "pm2.5_atm", "184291", "FLOAT", "12.4"
    )
    assert s_pm.type_tag == pdl.TypeTag_Float64
    assert s_pm.f64 == pytest.approx(12.4)
    assert s_pm.oid == "pm2.5_atm"
    assert s_pm.oid_index == "184291"

    s_humidity = pdl.Sample.from_purpleair_field(
        "humidity", "humidity", "184291", "INTEGER", "48"
    )
    assert s_humidity.type_tag == pdl.TypeTag_Int64
    assert s_humidity.i64 == 48

    payload = {
        "oid": "firmware_version",
        "index": "184291",
        "type": "STRING",
        "value": "7.02",
        "converted_value": "7.02",
    }
    s_from_json = pdl.Sample.from_json("firmware_version", json.dumps(payload))
    assert s_from_json.oid_index == "184291"
    assert s_from_json.snmp_type == "STRING"
    assert s_from_json.str_val == "7.02"


def test_data_logger_lifecycle_and_cli_runner(tmp_path: Path) -> None:
    cfg_dict = {
        "instance_name": "py-test-logger",
        "queue_capacity": 1000,
        "max_poll_Cycles": 2,
        "duts": [
            {
                "name": "patio-sensor",
                "dut_ip": "127.0.0.1",
                "enabled": True,
                "poll_interval_ms": 100,
                "snmp": {
                    "mode": "stub",
                    "version": "v1",
                    "sensor_index": 184291,
                },
                "metrics": [
                    {"name": "pm2_5_atm", "oid": "pm2.5_atm", "operation": "get"},
                    {"name": "humidity", "oid": "humidity", "operation": "get"},
                ],
            }
        ],
        "sinks": {
            "sqlite": {
                "enabled": True,
                "path": str(tmp_path / "py_test.sqlite"),
                "commit_batch_size": 1,
                "commit_interval_ms": 100,
            }
        },
        "gui": {"frontend": "auto", "theme": "dark"},
    }
    raw_cfg = json.dumps(cfg_dict, indent=2)

    rep = pdl.validate_config_json(raw_cfg)
    assert rep.valid is True
    assert rep.enabled_duts == 1

    logger = pdl.DataLogger.from_json_string(raw_cfg)
    batches = logger.run_once()
    assert len(batches) == 1
    assert len(batches[0].samples) == 2
    logger.flush()

    cfg_obj = pdl.LoggerConfig.from_json_string(raw_cfg)
    rows = pdl.inspect_configured_sinks(cfg_obj, 10, "patio-sensor", "")
    assert len(rows) == 2

    with pytest.raises(ValueError):
        pdl.LoggerConfig.from_json_string("{invalid json")

    cli_res = pdl.CliRunner.execute(pdl.StringVector(["version", "--json"]))
    assert cli_res.exit_code == 0
    assert json.loads(cli_res.stdout_text)["version"] == "2026.11.3a0"
