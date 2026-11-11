"""Tests for CLI subprocess bridge and streaming process lifecycle."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from purpleair_data_logger.gui.cli_bridge import (
    CliSubprocessBridge,
    resolve_cli_command,
)


def _create_minimal_config(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.json"
    doc = {
        "instance_name": "bridge-test",
        "queue_capacity": 500,
        "duts": [
            {
                "name": "sensor-01",
                "dut_ip": "127.0.0.1",
                "enabled": True,
                "poll_interval_ms": 100,
                "snmp": {
                    "mode": "stub",
                    "version": "v1",
                    "sensor_index": 131075,
                },
                "metrics": [
                    {"name": "pm2.5_atm", "oid": "pm2.5_atm", "operation": "get"},
                    {"name": "humidity", "oid": "humidity", "operation": "get"},
                ],
            }
        ],
        "sinks": [
            {
                "type": "sqlite3",
                "enabled": True,
                "path": str(tmp_path / "telemetry.sqlite"),
                "commit_every_n": 1,
                "commit_every_ms": 50,
            }
        ],
    }
    cfg.write_text(json.dumps(doc), encoding="utf-8")
    return cfg


def test_cli_bridge_complete_coverage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert resolve_cli_command("my-custom-cli --flag") == ["my-custom-cli", "--flag"]

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert resolve_cli_command() == [sys.executable, "cli"]
    monkeypatch.delattr(sys, "frozen")

    repo_root = Path(__file__).resolve().parent.parent
    build_bin = (
        repo_root
        / "build"
        / ("purpleair-data-logger.exe" if os.name == "nt" else "purpleair-data-logger")
    )
    had_existing_bin = build_bin.is_file()
    backup_bin = build_bin.with_suffix(".bak_test")
    if had_existing_bin:
        build_bin.rename(backup_bin)

    try:
        build_bin.parent.mkdir(parents=True, exist_ok=True)
        build_bin.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        build_bin.chmod(0o755)
        assert resolve_cli_command() == [str(build_bin)]
        build_bin.unlink()

        monkeypatch.setattr(
            "shutil.which",
            lambda cmd: (
                "/usr/local/bin/purpleair-data-logger"
                if cmd == "purpleair-data-logger"
                else None
            ),
        )
        assert resolve_cli_command() == ["/usr/local/bin/purpleair-data-logger"]

        monkeypatch.setattr("shutil.which", lambda cmd: None)
        assert resolve_cli_command() == [
            sys.executable,
            "-m",
            "purpleair_data_logger.cli",
        ]
    finally:
        if build_bin.is_file():
            build_bin.unlink()
        if had_existing_bin and backup_bin.is_file():
            backup_bin.rename(build_bin)

    missing_cfg = tmp_path / "sub" / "auto_init.json"
    bridge_missing = CliSubprocessBridge(missing_cfg, cli_override="false")
    assert missing_cfg.is_file()
    assert bridge_missing.load_config_dict()["duts"][0]["poll_interval_ms"] == 1000

    pref_cfg = tmp_path / "prefs.json"
    pref_doc = {"gui": {"cli_executable": "custom-cli", "max_log_lines": 80}}
    pref_cfg.write_text(json.dumps(pref_doc), encoding="utf-8")
    bridge_pref = CliSubprocessBridge(pref_cfg)
    assert bridge_pref._cli_override == "custom-cli"

    pref_cfg.write_text("{invalid json", encoding="utf-8")
    bridge_pref._sync_gui_preferences()

    bad_root_cfg = tmp_path / "bad_root.json"
    bad_root_cfg.write_text("[1, 2, 3]", encoding="utf-8")
    bridge_bad_root = CliSubprocessBridge(bad_root_cfg)
    with pytest.raises(ValueError, match="Root JSON configuration must be an object"):
        bridge_bad_root.load_config_dict()

    cfg = _create_minimal_config(tmp_path)
    bridge = CliSubprocessBridge(cfg)

    recorded_cmds: list[list[str]] = []

    def mock_exec(cmd: list[str], timeout: float = 30.0) -> dict[str, Any]:
        recorded_cmds.append(cmd)
        return {
            "ok": True,
            "exit_code": 0,
            "stdout": "{}",
            "stderr": "",
            "data": {},
            "audit": {},
        }

    monkeypatch.setattr(bridge, "_exec_cli", mock_exec)

    bridge.version_info()
    assert recorded_cmds[-1] == ["version", "--json"]

    bridge.schema()
    assert recorded_cmds[-1] == ["schema"]

    bridge.init_config_template("demo")
    assert recorded_cmds[-1] == ["init-config", "--template", "demo"]

    bridge.validate(config_text='{"test": 1}')
    assert recorded_cmds[-1] == ["validate", "--config-string", '{"test": 1}', "--json"]

    bridge.probe(dut_name="sensor-01")
    assert recorded_cmds[-1] == [
        "probe",
        "--config",
        str(bridge.config_path),
        "--json",
        "--dut",
        "sensor-01",
    ]

    bridge.inspect(limit=10, dut="s1", metric="pm2_5")
    assert recorded_cmds[-1] == [
        "inspect",
        "--config",
        str(bridge.config_path),
        "--limit",
        "10",
        "--json",
        "--dut",
        "s1",
        "--metric",
        "pm2_5",
    ]

    bridge.save_config_dict({"instance_name": "saved-cfg", "duts": [], "sinks": []})
    assert bridge.load_config_dict()["instance_name"] == "saved-cfg"

    monkeypatch.undo()
    cfg = _create_minimal_config(tmp_path)
    bridge_fresh = CliSubprocessBridge(cfg)

    def mock_run_bad_json(*args: Any, **kwargs: Any) -> Any:
        m = MagicMock()
        m.returncode = 0
        m.stdout = "{bad stdout json"
        m.stderr = "{bad stderr json"
        return m

    monkeypatch.setattr("subprocess.run", mock_run_bad_json)
    res_bad_json = bridge_fresh._exec_cli(["dummy"])
    assert res_bad_json["data"] is None

    def mock_run_stderr_json(*args: Any, **kwargs: Any) -> Any:
        m = MagicMock()
        m.returncode = 1
        m.stdout = ""
        m.stderr = '{"error": "from stderr"}'
        return m

    monkeypatch.setattr("subprocess.run", mock_run_stderr_json)
    res_stderr = bridge_fresh._exec_cli(["dummy"])
    assert res_stderr["data"] == {"error": "from stderr"}

    def mock_run_stderr_non_json(*args: Any, **kwargs: Any) -> Any:
        m = MagicMock()
        m.returncode = 1
        m.stdout = ""
        m.stderr = "plain text error without json"
        return m

    monkeypatch.setattr("subprocess.run", mock_run_stderr_non_json)
    res_stderr_plain = bridge_fresh._exec_cli(["dummy"])
    assert res_stderr_plain["data"] is None

    monkeypatch.undo()
    bridge = CliSubprocessBridge(cfg)

    start1 = bridge.start_run()
    assert start1["ok"] is True
    assert bridge.is_running() is True
    start2 = bridge.start_run()
    assert start2["already_running"] is True

    stop1 = bridge.stop_run()
    assert stop1["ok"] is True
    assert bridge.is_running() is False
    stop2 = bridge.stop_run()
    assert stop2["stopped"] is True

    def make_fake_proc():
        p = MagicMock()
        p.pid = 1234
        p.poll.return_value = None
        p.wait.return_value = 0
        p.returncode = 0
        p.stdout = iter([])
        p.stderr = iter([])
        return p

    bridge_win = CliSubprocessBridge(cfg)
    bridge_win.cli_base_command = lambda: ["purpleair-data-logger"]
    monkeypatch.setattr(os, "name", "nt")
    monkeypatch.setattr("signal.CTRL_BREAK_EVENT", 99, raising=False)

    p_spawn = make_fake_proc()
    monkeypatch.setattr("subprocess.Popen", lambda *args, **kwargs: p_spawn)
    bridge_win.start_run()
    bridge_win.stop_run()

    p_ctrl = make_fake_proc()
    bridge_win._run_proc = p_ctrl
    bridge_win.stop_run()
    p_ctrl.send_signal.assert_called_with(99)

    p_err = make_fake_proc()
    p_err.send_signal.side_effect = OSError("Failed to send CTRL_BREAK")
    bridge_win._run_proc = p_err
    bridge_win.stop_run()
    p_err.terminate.assert_called()

    p_no_break = make_fake_proc()
    monkeypatch.setattr("signal.CTRL_BREAK_EVENT", None, raising=False)
    bridge_win._run_proc = p_no_break
    bridge_win.stop_run()
    p_no_break.terminate.assert_called()

    fake_proc_timeout = MagicMock()
    fake_proc_timeout.pid = 9999
    fake_proc_timeout.poll.return_value = None
    fake_proc_timeout.wait.side_effect = [
        subprocess.TimeoutExpired(cmd="run", timeout=1.0),
        0,
    ]
    bridge_win._run_proc = fake_proc_timeout
    bridge_win.stop_run()
    fake_proc_timeout.kill.assert_called()

    monkeypatch.undo()
    bridge_ev = CliSubprocessBridge(cfg)

    bridge_ev.run_once()
    bridge_ev.request("sensor-01", "get", ["pm2.5_atm"])
    bridge_ev.set_oid("sensor-01", "name", "s", "TestSensor")

    batch_ev = {
        "event": "batch",
        "batch": {
            "ts_unix_ns": 0,
            "dut_name": "sensor1",
            "samples": [
                {"metric_name": "pm2_5", "type_tag": 2, "f64": 12.5},
                {"metric_name": "humidity", "type_tag": 1, "i64": 48},
                "non-dict-sample",
            ],
        },
    }
    bridge_ev._ingest_batch_event(batch_ev["batch"])
    assert "sensor1::pm2_5" in bridge_ev.snapshot()["series"]
    assert "sensor1::humidity" in bridge_ev.snapshot()["series"]

    mock_stream_proc = MagicMock()
    mock_stream_proc.stdout = iter(
        [
            "",
            "not json\n",
            "[1, 2, 3]\n",
            json.dumps({"event": "started", "stats": {"uptime_ms": 100}}) + "\n",
            json.dumps({"event": "stats", "stats": {"cycles_completed": 5}}) + "\n",
            json.dumps({"event": "stopped", "stats": {"running": False}}) + "\n",
            json.dumps(batch_ev) + "\n",
        ]
    )
    mock_stream_proc.wait.return_value = 0
    bridge_ev._read_run_stdout(mock_stream_proc)
    assert bridge_ev._latest_stats["cycles_completed"] == 5

    mock_stream_proc.stderr = iter(["Some warning line\n", ""])
    bridge_ev._read_run_stderr(mock_stream_proc)
    assert bridge_ev._latest_stats["last_error"] == "Some warning line"

    mock_none_proc = MagicMock()
    mock_none_proc.stdout = None
    mock_none_proc.stderr = None
    bridge_ev._read_run_stdout(mock_none_proc)
    bridge_ev._read_run_stderr(mock_none_proc)
