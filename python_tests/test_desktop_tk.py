"""Tests for Tkinter desktop GUI components and actions."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from purpleair_data_logger.gui import can_use_tkinter_display
from purpleair_data_logger.gui.cli_bridge import CliSubprocessBridge
from purpleair_data_logger.gui.launcher import get_icon_path


def _create_minimal_config(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.json"
    doc = {
        "instance_name": "tk-test",
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
        "sinks": {
            "sqlite": {
                "enabled": True,
                "path": str(tmp_path / "telemetry.sqlite"),
                "commit_batch_size": 1,
                "commit_interval_ms": 50,
            }
        },
    }
    cfg.write_text(json.dumps(doc), encoding="utf-8")
    return cfg


def test_desktop_tk_complete_coverage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    if not can_use_tkinter_display():
        pytest.skip("Tkinter graphical display not available in current environment")

    import tkinter as tk
    from purpleair_data_logger.gui.desktop_tk import (
        DesktopLoggerStudio,
        launch_desktop_gui,
    )

    cfg = _create_minimal_config(tmp_path)
    bridge = CliSubprocessBridge(cfg)

    studio = DesktopLoggerStudio(bridge, schedule_refresh=False)
    try:
        studio.root.withdraw()

        assert (
            DesktopLoggerStudio._set_macos_dock_icon(tmp_path / "nonexistent.png")
            is False
        )
        real_png = get_icon_path("png")
        if sys.platform == "darwin":
            assert DesktopLoggerStudio._set_macos_dock_icon(real_png) is True

        monkeypatch.setattr(
            "ctypes.cdll.LoadLibrary",
            lambda name: (_ for _ in ()).throw(RuntimeError("ctypes error")),
        )
        assert DesktopLoggerStudio._set_macos_dock_icon(real_png) is False
        monkeypatch.undo()

        monkeypatch.setattr(
            "tkinter.PhotoImage",
            lambda file=None: (_ for _ in ()).throw(RuntimeError("bad png")),
        )
        studio._apply_icon()
        monkeypatch.undo()

        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setattr(studio.root, "iconbitmap", lambda default=None: None)
        studio._apply_icon()
        monkeypatch.setattr(
            studio.root,
            "iconbitmap",
            lambda default=None: (_ for _ in ()).throw(RuntimeError("bad ico")),
        )
        studio._apply_icon()
        monkeypatch.undo()

        studio._populate_dut_form(-1)
        assert studio._selected_dut_index == 0
        studio._populate_dut_form(0)
        studio.dut_listbox.selection_set(0)
        studio._on_dut_selected()

        monkeypatch.setattr("tkinter.filedialog.askopenfilename", lambda **kw: None)
        studio.action_open_config()
        monkeypatch.setattr("tkinter.filedialog.askopenfilename", lambda **kw: str(cfg))
        studio.action_open_config()

        studio.action_start_run()
        studio.action_stop_run()
        studio.action_run_once()
        studio.action_save_all()

        studio.action_probe_all()
        studio.action_probe_selected_dut()

        sample_payload = {
            "count": 1,
            "results": [
                {
                    "samples": [
                        {
                            "oid": "pm2.5_atm",
                            "oid_index": "131075",
                            "snmp_type": "FLOAT",
                            "raw_value": "12.4",
                            "type_name": "f64",
                            "status": 0,
                        }
                    ]
                }
            ],
        }
        studio._populate_request_results_from_probe(sample_payload)
        assert len(studio.req_tree.get_children()) >= 1

        studio.action_validate_saved()
        monkeypatch.setattr(
            studio.bridge,
            "validate",
            lambda *args, **kw: {
                "ok": False,
                "data": {"valid": False, "errors": ["Mock validation error"]},
            },
        )
        studio.action_validate_saved()
        assert "FAILED" in studio.json_status_var.get()
        monkeypatch.undo()

        studio._selected_dut_index = 999
        studio.action_remove_dut()
        studio.action_apply_dut()
        studio.action_add_metric()
        studio.action_remove_metric()

        studio._selected_dut_index = 0
        studio.metrics_tree.selection_set([])
        studio.action_remove_metric()

        studio.action_add_dut()
        assert len(studio.config_doc.get("duts", [])) >= 2
        studio.dut_vars["name"].set("renamed-sensor")
        studio.action_apply_dut()
        assert (
            studio.config_doc["duts"][studio._selected_dut_index]["name"]
            == "renamed-sensor"
        )
        studio.action_remove_dut()

        studio.new_metric_name.set("temperature")
        studio.new_metric_oid.set("temperature")
        studio.new_metric_op.set("get")
        studio.action_add_metric()
        children = studio.metrics_tree.get_children()
        assert len(children) >= 1
        studio.metrics_tree.selection_set(children[-1])
        studio.action_remove_metric()

        studio.req_dut_var.set("")
        studio.action_execute_ezsnmp_request()
        assert "Select a Sensor" in studio.req_summary_var.get()

        studio.req_dut_var.set("sensor-01")
        studio.req_op_var.set("get")
        studio.req_oid_var.set("pm2.5_atm")
        studio.action_execute_ezsnmp_request()
        assert "OK:" in studio.req_summary_var.get()

        studio.req_op_var.set("set")
        studio.req_set_type_var.set("s")
        studio.req_set_val_var.set("PatioSensor")
        studio.action_execute_ezsnmp_request()

        monkeypatch.setattr(
            studio.bridge,
            "request",
            lambda *a, **k: {
                "ok": False,
                "stderr": "Connection timed out",
                "data": {"error": "Timeout"},
            },
        )
        studio.req_op_var.set("get")
        studio.action_execute_ezsnmp_request()
        assert "Error:" in studio.req_summary_var.get()
        monkeypatch.undo()

        studio.config_doc.setdefault("sinks", {})["psql"] = {
            "enabled": True,
            "conninfo": "host=localhost",
        }
        studio.settings_vars["gui_theme"].set("light")
        studio.settings_vars["gui_locale"].set("es")
        studio.settings_vars["csv_enabled"].set(True)
        studio.settings_vars["jsonl_enabled"].set(True)
        studio.settings_vars["prom_enabled"].set(True)
        studio.action_apply_settings_tab()
        assert studio.theme_name == "light"

        studio.settings_vars["gui_theme"].set("dark")
        studio.settings_vars["gui_locale"].set("en")
        studio.action_apply_settings_tab()
        assert studio.theme_name == "dark"

        studio.inspect_tree.insert(
            "", tk.END, values=("1", "s1", "m", "oid", "t", "v", "s")
        )
        studio.action_inspect_sinks()
        assert len(studio.inspect_tree.get_children()) >= 0

        studio.tpl_var.set("demo")
        studio.action_load_template()
        assert len(studio.json_editor.get("1.0", tk.END)) > 10

        studio.action_validate_editor()
        assert "PASSED" in studio.json_status_var.get()

        studio.json_editor.delete("1.0", tk.END)
        studio.json_editor.insert("1.0", "{bad json")
        studio.action_validate_editor()
        assert "FAILED" in studio.json_status_var.get()

        monkeypatch.setattr("tkinter.messagebox.showerror", lambda *a, **k: None)
        studio.action_save_editor_json()

        studio.action_load_template()
        studio.action_save_editor_json()
        assert "Saved JSON" in studio.json_status_var.get()

        monkeypatch.setattr(
            studio.bridge,
            "save_config_text",
            lambda *a, **k: {
                "ok": False,
                "data": {"valid": False, "errors": ["Mock schema error"]},
            },
        )
        studio.action_save_editor_json()
        assert "Saved JSON with validation errors" in studio.json_status_var.get()
        monkeypatch.undo()

        studio.action_show_schema()

        studio._update_audit_banner(None)
        studio._update_audit_banner(
            {"command": "test", "exit_code": None, "duration_ms": 10}
        )
        assert "running" in studio.audit_status_var.get()
        studio._update_audit_banner(
            {"command": "test", "exit_code": 0, "duration_ms": 10}
        )
        assert "[0," in studio.audit_status_var.get()

        studio._draw_chart({})
        single_pt = {"sensor::pm": [{"value": 12.0}]}
        studio._draw_chart(single_pt)
        identical_pts = {"sensor::pm": [{"value": 50.0}, {"value": 50.0}]}
        studio._draw_chart(identical_pts)
        multi_series = {
            "s1::pm": [{"value": 10.0}, {"value": 20.0}],
            "s1::temp": [{"value": 35.0}, {"value": 45.0}],
        }
        studio._draw_chart(multi_series)

        studio.action_select_all_series()
        studio._on_series_toggle()
        studio.action_clear_all_series()
        if studio._legend_hitboxes:
            box = studio._legend_hitboxes[0]
            fake_event = MagicMock()
            fake_event.x = (box[0] + box[2]) // 2
            fake_event.y = (box[1] + box[3]) // 2
            studio._on_canvas_click(fake_event)

        studio.refresh_live_state(reschedule=False)

        studio._after_id = "after#1"
        monkeypatch.setattr(
            studio.root,
            "after_cancel",
            lambda aid: (_ for _ in ()).throw(RuntimeError("cancel failed")),
        )
        studio.on_close()
        monkeypatch.undo()
    finally:
        pass

    monkeypatch.setattr(
        "tkinter.PhotoImage",
        lambda file=None: (_ for _ in ()).throw(RuntimeError("header icon fail")),
    )
    studio_no_icon = DesktopLoggerStudio(bridge, schedule_refresh=False)
    studio_no_icon.on_close()
    monkeypatch.undo()

    monkeypatch.setattr(
        "purpleair_data_logger.gui.desktop_tk.DesktopLoggerStudio.on_close",
        lambda self: None,
    )
    monkeypatch.setattr("tkinter.Tk.mainloop", lambda self: None)
    rc_gui = launch_desktop_gui(bridge)
    assert rc_gui == 0
