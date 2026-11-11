"""Tests for CLI dispatch, desktop entrypoint, and GUI main command routing."""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path
from typing import Any

import pytest

import purpleair_data_logger.cli as cli
import purpleair_data_logger.entry_desktop as entry_desktop
from purpleair_data_logger.gui import (
    can_use_tkinter_display,
    main as gui_main,
    select_frontend,
)


def _create_minimal_config(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.json"
    doc = {
        "instance_name": "test-logger",
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
        "gui": {
            "frontend": "auto",
            "host": "127.0.0.1",
            "port": 0,
            "theme": "dark",
            "max_log_lines": 200,
            "cli_executable": "",
        },
    }
    cfg.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return cfg


def test_package_and_gui_mains_and_runpy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "purpleair_data_logger.cli.CliRunner.run",
        staticmethod(lambda vec: 0),
    )
    monkeypatch.setattr(sys, "argv", ["purpleair-data-logger", "version"])

    with pytest.raises(SystemExit) as exc:
        runpy.run_module("purpleair_data_logger", run_name="__main__")
    assert exc.value.code == 0

    monkeypatch.setattr("purpleair_data_logger.gui.main", lambda argv=None: 84)
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("purpleair_data_logger.gui", run_name="__main__")
    assert exc.value.code == 84

    with pytest.raises(SystemExit) as exc:
        runpy.run_module("purpleair_data_logger.cli", run_name="__main__")
    assert exc.value.code == 0

    with pytest.raises(SystemExit) as exc:
        runpy.run_module("purpleair_data_logger.entry_desktop", run_name="__main__")
    assert exc.value.code == 0


def test_cli_dispatch_and_gui_forwarding(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[list[str]] = []

    def mock_gui_main(argv: list[str] | None = None) -> int:
        captured.append(list(argv or []))
        return 99

    monkeypatch.setattr("purpleair_data_logger.gui.main", mock_gui_main)
    rc = cli.main(["gui", "--port", "1234"])
    assert rc == 99
    assert captured == [["--port", "1234"]]

    rc_gui = cli.main_gui(["--port", "5678"])
    assert rc_gui == 99
    assert captured[-1] == ["--port", "5678"]


def test_entry_desktop_all_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    gui_captured: list[list[str]] = []
    cli_captured: list[list[str]] = []

    monkeypatch.setattr(
        "purpleair_data_logger.gui.main",
        lambda argv=None: (gui_captured.append(list(argv or [])), 1)[1],
    )
    monkeypatch.setattr(
        "purpleair_data_logger.cli.main",
        lambda argv=None: (cli_captured.append(list(argv or [])), 2)[1],
    )

    assert entry_desktop.main([]) == 1
    assert gui_captured[-1] == []

    assert entry_desktop.main(["-psn_0_98765"]) == 1
    assert gui_captured[-1] == []

    assert entry_desktop.main(["gui", "--frontend", "web"]) == 1
    assert gui_captured[-1] == ["--frontend", "web"]

    assert entry_desktop.main(["--custom-option", "value"]) == 1
    assert gui_captured[-1] == ["--custom-option", "value"]

    assert entry_desktop.main(["cli", "run", "-c", "test.json"]) == 2
    assert cli_captured[-1] == ["run", "-c", "test.json"]

    for sub in (
        "run",
        "validate",
        "probe",
        "request",
        "set",
        "inspect",
        "schema",
        "version",
    ):
        assert entry_desktop.main([sub, "--help"]) == 2
        assert cli_captured[-1] == [sub, "--help"]


def test_can_use_tkinter_display_and_select_frontend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    orig_import = __import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "tkinter":
            raise ImportError("Mocked tkinter missing")
        return orig_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", mock_import)
    assert can_use_tkinter_display() is False

    monkeypatch.undo()
    monkeypatch.setattr(sys, "platform", "win32")
    assert can_use_tkinter_display() is True
    monkeypatch.setattr(sys, "platform", "darwin")
    assert can_use_tkinter_display() is True

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    assert can_use_tkinter_display() is False
    assert select_frontend("auto") == "web"

    monkeypatch.setenv("DISPLAY", ":0")
    assert can_use_tkinter_display() is True
    assert select_frontend("auto") == "tk"

    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    assert can_use_tkinter_display() is True

    assert select_frontend("tk") == "tk"
    assert select_frontend("web") == "web"


def test_gui_main_cli_dispatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = _create_minimal_config(tmp_path)

    launcher_dir = tmp_path / "installed_launcher"
    rc = gui_main(["--install-launcher", "--launcher-dir", str(launcher_dir)])
    assert rc == 0
    assert launcher_dir.exists()

    tk_called: list[Any] = []
    monkeypatch.setattr(
        "purpleair_data_logger.gui.desktop_tk.launch_desktop_gui",
        lambda bridge, locale_mgr=None: (tk_called.append(bridge), 11)[1],
    )
    rc_tk = gui_main(["-c", str(cfg), "--frontend", "tk", "--locale", "en"])
    assert rc_tk == 11
    assert len(tk_called) == 1

    web_called: list[dict[str, Any]] = []

    def mock_launch_desktop_raise(bridge: Any, locale_mgr: Any = None) -> int:
        raise RuntimeError("No Tk display available")

    def mock_launch_web(
        bridge: Any,
        host: str = "127.0.0.1",
        port: int = 8765,
        open_browser: bool = True,
        locale_mgr: Any = None,
    ) -> int:
        web_called.append(
            {
                "host": host,
                "port": port,
                "open_browser": open_browser,
                "locale": locale_mgr.locale,
            }
        )
        return 22

    monkeypatch.setattr(
        "purpleair_data_logger.gui.desktop_tk.launch_desktop_gui",
        mock_launch_desktop_raise,
    )
    monkeypatch.setattr(
        "purpleair_data_logger.gui.server.launch_web_gui", mock_launch_web
    )

    rc_fallback = gui_main(["-c", str(cfg), "--frontend", "tk"])
    assert rc_fallback == 22
    assert len(web_called) == 1

    rc_web = gui_main(
        [
            "-c",
            str(cfg),
            "--frontend",
            "web",
            "--host",
            "0.0.0.0",
            "--port",
            "9999",
            "--no-browser",
            "--locale",
            "es",
        ]
    )
    assert rc_web == 22
    assert web_called[-1] == {
        "host": "0.0.0.0",
        "port": 9999,
        "open_browser": False,
        "locale": "es",
    }
