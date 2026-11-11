"""Tests for Studio HTTP server API endpoints and web GUI launcher."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path
from typing import Any

import pytest

from purpleair_data_logger.gui.cli_bridge import CliSubprocessBridge
from purpleair_data_logger.gui.server import (
    create_web_server,
    launch_web_gui,
)


def _create_minimal_config(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.json"
    doc = {
        "instance_name": "server-test",
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


def test_server_complete_coverage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _create_minimal_config(tmp_path)
    bridge = CliSubprocessBridge(cfg)
    srv = create_web_server(bridge, host="127.0.0.1", port=0)
    host, port = srv.server_address[:2]
    base_url = f"http://{host}:{port}"

    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()

    try:
        with urllib.request.urlopen(f"{base_url}/api/status") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True

        with urllib.request.urlopen(f"{base_url}/api/locale?locale=en") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True
            assert data["locale"] == "en"

        with urllib.request.urlopen(f"{base_url}/api/config") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True
            assert "config" in data

        with urllib.request.urlopen(f"{base_url}/api/version") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True

        with urllib.request.urlopen(f"{base_url}/api/schema") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True

        with urllib.request.urlopen(f"{base_url}/api/template?name=demo") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True
            assert data["template"] == "demo"

        with urllib.request.urlopen(
            f"{base_url}/api/inspect?limit=5&dut=sensor-01&metric=pm2.5_atm"
        ) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True

        with pytest.raises(urllib.error.HTTPError) as exc_get_bad:
            urllib.request.urlopen(f"{base_url}/api/inspect?limit=not_an_int")
        assert exc_get_bad.value.code == HTTPStatus.BAD_REQUEST

        for asset in ("index.html", "styles.css", "app.js", "app_icon.png"):
            with urllib.request.urlopen(f"{base_url}/{asset}") as resp:
                assert resp.status == 200

        with pytest.raises(urllib.error.HTTPError) as exc_404:
            urllib.request.urlopen(f"{base_url}/../../../nonexistent_file.txt")
        assert exc_404.value.code == HTTPStatus.NOT_FOUND

        post_cfg_raw = urllib.request.Request(
            f"{base_url}/api/config",
            data=json.dumps(
                {
                    "raw": json.dumps(
                        {
                            "instance_name": "raw-test",
                            "duts": [
                                {
                                    "name": "s1",
                                    "dut_ip": "127.0.0.1",
                                    "enabled": True,
                                    "poll_interval_ms": 200,
                                    "snmp": {"mode": "stub", "sensor_index": 131075},
                                    "metrics": [
                                        {
                                            "name": "pm",
                                            "oid": "pm2.5_atm",
                                            "operation": "get",
                                        }
                                    ],
                                }
                            ],
                            "sinks": {
                                "sqlite": {
                                    "enabled": True,
                                    "path": str(tmp_path / "telemetry.sqlite"),
                                }
                            },
                        }
                    )
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(post_cfg_raw) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True

        post_cfg_obj = urllib.request.Request(
            f"{base_url}/api/config",
            data=json.dumps(
                {
                    "config": {
                        "instance_name": "obj-test",
                        "duts": [
                            {
                                "name": "sensor-01",
                                "dut_ip": "127.0.0.1",
                                "enabled": True,
                                "poll_interval_ms": 300,
                                "snmp": {"mode": "stub", "sensor_index": 131075},
                                "metrics": [
                                    {
                                        "name": "pm2.5_atm",
                                        "oid": "pm2.5_atm",
                                        "operation": "get",
                                    }
                                ],
                            }
                        ],
                        "sinks": {
                            "sqlite": {
                                "enabled": True,
                                "path": str(tmp_path / "telemetry.sqlite"),
                            }
                        },
                    }
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(post_cfg_obj) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True

        post_cfg_bad = urllib.request.Request(
            f"{base_url}/api/config",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as exc_400:
            urllib.request.urlopen(post_cfg_bad)
        assert exc_400.value.code == HTTPStatus.BAD_REQUEST

        post_val = urllib.request.Request(
            f"{base_url}/api/validate",
            data=json.dumps({"raw": bridge.load_config_text()}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(post_val) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert "ok" in data

        post_probe = urllib.request.Request(
            f"{base_url}/api/probe",
            data=json.dumps({"dut": "sensor-01"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(post_probe) as resp:
            assert resp.status == 200

        post_req_str = urllib.request.Request(
            f"{base_url}/api/request",
            data=json.dumps(
                {
                    "dut": "sensor-01",
                    "operation": "get",
                    "oids": "pm2.5_atm",
                    "record": True,
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(post_req_str) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert "ok" in data

        post_set = urllib.request.Request(
            f"{base_url}/api/set",
            data=json.dumps(
                {
                    "dut": "sensor-01",
                    "oid": "name",
                    "set_type": "s",
                    "value": "PatioSensor",
                    "record": True,
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(post_set) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert "ok" in data

        post_start = urllib.request.Request(
            f"{base_url}/api/run/start",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(post_start) as resp:
            assert json.loads(resp.read().decode("utf-8"))["ok"] is True

        post_stop = urllib.request.Request(
            f"{base_url}/api/run/stop",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(post_stop) as resp:
            assert json.loads(resp.read().decode("utf-8"))["ok"] is True

        post_once = urllib.request.Request(
            f"{base_url}/api/run/once",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(post_once) as resp:
            assert json.loads(resp.read().decode("utf-8"))["ok"] is True

        post_loc = urllib.request.Request(
            f"{base_url}/api/locale",
            data=json.dumps({"locale": "es"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(post_loc) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True
            assert data["locale"] == "es"

        post_unknown = urllib.request.Request(
            f"{base_url}/api/nonexistent_endpoint",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as exc_unk:
            urllib.request.urlopen(post_unknown)
        assert exc_unk.value.code == HTTPStatus.NOT_FOUND

        post_non_dict = urllib.request.Request(
            f"{base_url}/api/validate",
            data=b"[1, 2, 3]",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as exc_non_dict:
            urllib.request.urlopen(post_non_dict)
        assert exc_non_dict.value.code == HTTPStatus.BAD_REQUEST

    finally:
        bridge.stop_run()
        srv.shutdown()
        srv.server_close()

    def mock_serve_forever(self: Any) -> None:
        raise KeyboardInterrupt()

    def mock_browser_open_error(url: str) -> bool:
        raise RuntimeError("No browser")

    monkeypatch.setattr(
        "purpleair_data_logger.gui.server.StudioHttpServer.serve_forever",
        mock_serve_forever,
    )
    monkeypatch.setattr("webbrowser.open", mock_browser_open_error)
    rc_launch = launch_web_gui(bridge, host="127.0.0.1", port=0, open_browser=True)
    assert rc_launch == 0
