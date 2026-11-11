"""Pure CLI subprocess + JSON bridge powering all purpleair_data_logger GUIs.

All Graphical User Interfaces (native tkinter.ttk desktop and Browser Web Studio)
interact exclusively with the `purpleair-data-logger` CLI behind the scenes and store
100% of settings in JSON configuration files.
"""

from __future__ import annotations

import collections
import datetime as dt
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any


def _utc_iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def resolve_cli_command(cli_override: str = "") -> list[str]:
    """Locate the purpleair-data-logger CLI command across Linux, macOS, and Windows."""
    if cli_override.strip():
        return shlex.split(cli_override, posix=(os.name != "nt"))

    if getattr(sys, "frozen", False):
        return [sys.executable, "cli"]

    repo_root = Path(__file__).resolve().parent.parent.parent
    exe_suffix = ".exe" if os.name == "nt" else ""
    local_build_bin = repo_root / "build" / f"purpleair-data-logger{exe_suffix}"
    if local_build_bin.is_file() and os.access(local_build_bin, os.X_OK):
        return [str(local_build_bin)]

    which_bin = shutil.which("purpleair-data-logger")
    if which_bin:
        return [which_bin]

    return [sys.executable, "-m", "purpleair_data_logger.cli"]


class CliSubprocessBridge:
    """Thread-safe controller that drives `purpleair-data-logger` strictly via CLI + JSON."""

    def __init__(self, config_path: str | Path, cli_override: str = "") -> None:
        self.config_path = Path(config_path).expanduser().resolve()
        self._lock = threading.RLock()
        self._cli_override = cli_override
        self._audit_log: collections.deque[dict[str, Any]] = collections.deque(
            maxlen=250
        )
        self._cli_lines: collections.deque[str] = collections.deque(maxlen=500)
        self._recent_batches: collections.deque[dict[str, Any]] = collections.deque(
            maxlen=100
        )
        self._metric_series: dict[str, collections.deque[dict[str, Any]]] = {}

        self._run_proc: subprocess.Popen[str] | None = None
        self._stdout_thread: threading.Thread | None = None
        self._stderr_thread: threading.Thread | None = None
        self._latest_stats: dict[str, Any] = {
            "running": False,
            "cycles_completed": 0,
            "processed_batches": 0,
            "processed_samples": 0,
            "dropped_batches": 0,
            "poll_errors": 0,
            "sink_errors": 0,
            "queue_depth": 0,
            "uptime_ms": 0,
            "last_error": "",
        }

        self._ensure_config_exists()
        self._sync_gui_preferences()

    def _ensure_config_exists(self) -> None:
        if self.config_path.is_file():
            return
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        res = self._exec_cli(
            [
                "init-config",
                "--template",
                "demo",
                "--output",
                str(self.config_path),
                "--json",
            ]
        )
        if res["exit_code"] != 0 and not self.config_path.is_file():
            default_doc = {
                "instance_name": "purpleair-demo",
                "queue_capacity": 4096,
                "duts": [
                    {
                        "name": "demo-sensor-01",
                        "dut_ip": "127.0.0.1",
                        "poll_interval_ms": 1000,
                        "enabled": True,
                        "purpleair": {"mode": "stub", "sensor_index": 131075},
                        "metrics": [
                            {
                                "name": "pm2.5_atm",
                                "field": "pm2.5_atm",
                                "operation": "get",
                            },
                            {
                                "name": "humidity",
                                "field": "humidity",
                                "operation": "get",
                            },
                        ],
                    }
                ],
                "sinks": {
                    "sqlite": {
                        "enabled": True,
                        "path": "./data/purpleair_demo.sqlite3",
                    },
                },
                "gui": {"frontend": "auto", "theme": "dark"},
            }
            self.config_path.write_text(
                json.dumps(default_doc, indent=2) + "\n", encoding="utf-8"
            )

    def _sync_gui_preferences(self) -> None:
        try:
            cfg = json.loads(self.config_path.read_text(encoding="utf-8"))
            gui = cfg.get("gui", {}) if isinstance(cfg, dict) else {}
            max_lines = int(gui.get("max_log_lines", 500))
            if max_lines >= 50:
                with self._lock:
                    self._cli_lines = collections.deque(
                        self._cli_lines, maxlen=max_lines
                    )
            if not self._cli_override and isinstance(gui.get("cli_executable"), str):
                if gui["cli_executable"].strip():
                    self._cli_override = gui["cli_executable"].strip()
        except Exception:
            pass

    def cli_base_command(self) -> list[str]:
        return resolve_cli_command(self._cli_override)

    @staticmethod
    def _format_cmd_display(cmd: list[str]) -> str:
        if os.name == "nt":
            return subprocess.list2cmdline(cmd)
        return " ".join(shlex.quote(part) for part in cmd)

    def _record_audit(
        self,
        cmd: list[str],
        exit_code: int | None,
        duration_ms: float,
        note: str = "",
    ) -> dict[str, Any]:
        entry = {
            "timestamp": _utc_iso_now(),
            "command": self._format_cmd_display(cmd),
            "argv": list(cmd),
            "exit_code": exit_code,
            "duration_ms": round(duration_ms, 2),
            "note": note,
        }
        with self._lock:
            self._audit_log.appendleft(entry)
        return entry

    def _exec_cli(self, sub_args: list[str], timeout: float = 30.0) -> dict[str, Any]:
        cmd = self.cli_base_command() + sub_args
        t0 = time.perf_counter()
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        audit = self._record_audit(cmd, proc.returncode, elapsed_ms)

        parsed_json: Any = None
        raw_out = proc.stdout.strip()
        raw_err = proc.stderr.strip()
        if raw_out:
            try:
                parsed_json = json.loads(raw_out)
            except json.JSONDecodeError:
                parsed_json = None
        elif raw_err:
            try:
                parsed_json = json.loads(raw_err)
            except json.JSONDecodeError:
                parsed_json = None

        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "data": parsed_json,
            "audit": audit,
        }

    # --- JSON Configuration File Access ---

    def load_config_text(self) -> str:
        return self.config_path.read_text(encoding="utf-8")

    def load_config_dict(self) -> dict[str, Any]:
        data = json.loads(self.load_config_text())
        if not isinstance(data, dict):
            raise ValueError("Root JSON configuration must be an object")
        return data

    def save_config_text(self, raw_json: str) -> dict[str, Any]:
        parsed = json.loads(raw_json)
        formatted = json.dumps(parsed, indent=2) + "\n"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.config_path.with_suffix(self.config_path.suffix + ".tmp")
        tmp_path.write_text(formatted, encoding="utf-8")
        os.replace(tmp_path, self.config_path)
        self._sync_gui_preferences()
        return self.validate()

    def save_config_dict(self, config_obj: dict[str, Any]) -> dict[str, Any]:
        return self.save_config_text(json.dumps(config_obj, indent=2))

    # --- One-Shot CLI Operations ---

    def version_info(self) -> dict[str, Any]:
        return self._exec_cli(["version", "--json"])

    def schema(self) -> dict[str, Any]:
        return self._exec_cli(["schema"])

    def init_config_template(self, template_name: str = "demo") -> dict[str, Any]:
        return self._exec_cli(["init-config", "--template", template_name])

    def validate(self, config_text: str | None = None) -> dict[str, Any]:
        if config_text is not None:
            return self._exec_cli(
                ["validate", "--config-string", config_text, "--json"]
            )
        return self._exec_cli(["validate", "--config", str(self.config_path), "--json"])

    def probe(self, dut_name: str = "") -> dict[str, Any]:
        args = ["probe", "--config", str(self.config_path), "--json"]
        if dut_name.strip():
            args.extend(["--dut", dut_name.strip()])
        return self._exec_cli(args, timeout=60.0)

    def request(
        self,
        dut_name: str,
        operation: str,
        oids: list[str],
        max_repeaters: int = 10,
        record: bool = False,
    ) -> dict[str, Any]:
        args = [
            "request",
            "--config",
            str(self.config_path),
            "--dut",
            dut_name,
            "--op",
            operation,
            "--max-repeaters",
            str(int(max_repeaters)),
            "--json",
        ]
        for oid in oids:
            if oid.strip():
                args.extend(["--oid", oid.strip()])
        if record:
            args.append("--record")
        res = self._exec_cli(args, timeout=60.0)
        if res["ok"] and isinstance(res.get("data"), dict):
            batch = res["data"].get("batch")
            if isinstance(batch, dict):
                self._ingest_batch_event(batch)
        return res

    def set_oid(
        self,
        dut_name: str,
        oid: str,
        set_type: str,
        value: str,
        record: bool = False,
    ) -> dict[str, Any]:
        args = [
            "set",
            "--config",
            str(self.config_path),
            "--dut",
            dut_name,
            "--oid",
            oid.strip(),
            "--type",
            set_type.strip() or "s",
            "--value",
            value,
            "--json",
        ]
        if record:
            args.append("--record")
        res = self._exec_cli(args, timeout=60.0)
        if res["ok"] and isinstance(res.get("data"), dict):
            batch = res["data"].get("batch")
            if isinstance(batch, dict):
                self._ingest_batch_event(batch)
        return res

    def run_once(self) -> dict[str, Any]:
        res = self._exec_cli(
            ["run", "--config", str(self.config_path), "--once", "--json"], timeout=60.0
        )
        if res["ok"] and isinstance(res.get("data"), dict):
            stats = res["data"].get("stats")
            if isinstance(stats, dict):
                with self._lock:
                    self._latest_stats.update(stats)
            for b in res["data"].get("batches", []):
                if isinstance(b, dict):
                    self._ingest_batch_event(b)
        return res

    def inspect(
        self,
        limit: int = 50,
        dut: str = "",
        metric: str = "",
    ) -> dict[str, Any]:
        args = [
            "inspect",
            "--config",
            str(self.config_path),
            "--limit",
            str(max(1, int(limit))),
            "--json",
        ]
        if dut.strip():
            args.extend(["--dut", dut.strip()])
        if metric.strip():
            args.extend(["--metric", metric.strip()])
        return self._exec_cli(args)

    # --- Streaming Background CLI `run --json` Process Management ---

    def is_running(self) -> bool:
        with self._lock:
            return self._run_proc is not None and self._run_proc.poll() is None

    def start_run(self) -> dict[str, Any]:
        with self._lock:
            if self._run_proc is not None and self._run_proc.poll() is None:
                return {"ok": True, "already_running": True, "pid": self._run_proc.pid}

            cmd = self.cli_base_command() + [
                "run",
                "--config",
                str(self.config_path),
                "--json",
            ]
            popen_kwargs: dict[str, Any] = {
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "text": True,
                "bufsize": 1,
            }
            if os.name == "nt":
                popen_kwargs["creationflags"] = getattr(
                    subprocess, "CREATE_NEW_PROCESS_GROUP", 0
                )

            proc = subprocess.Popen(cmd, **popen_kwargs)
            self._run_proc = proc
            self._latest_stats["running"] = True
            audit = self._record_audit(cmd, None, 0.0, note=f"spawned pid={proc.pid}")

            self._stdout_thread = threading.Thread(
                target=self._read_run_stdout, args=(proc,), daemon=True
            )
            self._stderr_thread = threading.Thread(
                target=self._read_run_stderr, args=(proc,), daemon=True
            )
            self._stdout_thread.start()
            self._stderr_thread.start()

            return {"ok": True, "pid": proc.pid, "audit": audit}

    def stop_run(self, timeout: float = 8.0) -> dict[str, Any]:
        with self._lock:
            proc = self._run_proc
        if proc is None:
            with self._lock:
                self._latest_stats["running"] = False
            return {"ok": True, "stopped": True, "exit_code": 0}

        t0 = time.perf_counter()
        if proc.poll() is None:
            try:
                if os.name == "nt":
                    ctrl_break = getattr(signal, "CTRL_BREAK_EVENT", None)
                    if ctrl_break is not None:
                        try:
                            proc.send_signal(ctrl_break)
                        except OSError:
                            proc.terminate()
                    else:
                        proc.terminate()
                else:
                    proc.send_signal(signal.SIGINT)
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2.0)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        rc = proc.returncode
        with self._lock:
            self._latest_stats["running"] = False
            self._run_proc = None
        audit = self._record_audit(
            ["<stop-cli-run>", f"pid={proc.pid}"], rc, elapsed_ms
        )
        return {"ok": True, "stopped": True, "exit_code": rc, "audit": audit}

    def _ingest_batch_event(self, batch: dict[str, Any]) -> None:
        ts_ns = int(batch.get("ts_unix_ns") or batch.get("timestamp_ns") or 0) or int(
            time.time() * 1e9
        )
        dut_name = str(batch.get("dut_name", "unknown"))
        with self._lock:
            self._recent_batches.appendleft(batch)
            for s in batch.get("samples", []):
                if not isinstance(s, dict):
                    continue
                tag = s.get("type_tag")
                val: float | None = None
                if tag == 1 or s.get("type_name") == "i64":
                    val = float(s.get("i64", 0))
                elif tag == 2 or s.get("type_name") == "f64":
                    val = float(s.get("f64", 0.0))
                if val is not None:
                    series_key = (
                        f"{dut_name}::{s.get('metric_name', s.get('oid', 'metric'))}"
                    )
                    ring = self._metric_series.get(series_key)
                    if ring is None:
                        ring = collections.deque(maxlen=120)
                        self._metric_series[series_key] = ring
                    ring.append({"ts_ms": int(ts_ns // 1_000_000), "value": val})

    def _read_run_stdout(self, proc: subprocess.Popen[str]) -> None:
        if proc.stdout is None:
            return
        for raw_line in proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            with self._lock:
                self._cli_lines.append(line)
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(ev, dict):
                continue
            ev_type = ev.get("event")
            if ev_type in ("started", "stats", "stopped", "batch"):
                stats_obj = ev.get("stats")
                if isinstance(stats_obj, dict):
                    with self._lock:
                        self._latest_stats.update(stats_obj)
                        if ev_type == "stopped":
                            self._latest_stats["running"] = False
            if ev_type == "batch":
                b = ev.get("batch")
                if isinstance(b, dict):
                    self._ingest_batch_event(b)

        rc = proc.wait()
        with self._lock:
            if self._run_proc is proc:
                self._latest_stats["running"] = False
                self._run_proc = None
            self._cli_lines.append(f'{{"event":"process_exit","exit_code":{rc}}}')

    def _read_run_stderr(self, proc: subprocess.Popen[str]) -> None:
        if proc.stderr is None:
            return
        for raw_line in proc.stderr:
            line = raw_line.strip()
            if line:
                with self._lock:
                    self._cli_lines.append(f"[stderr] {line}")
                    self._latest_stats["last_error"] = line

    def snapshot(self) -> dict[str, Any]:
        """Return a thread-safe live telemetry & CLI audit snapshot for GUI rendering."""
        running = self.is_running()
        with self._lock:
            stats = dict(self._latest_stats)
            stats["running"] = running
            series = {k: list(v) for k, v in self._metric_series.items()}
            return {
                "config_path": str(self.config_path),
                "cli_command": self._format_cmd_display(self.cli_base_command()),
                "running": running,
                "stats": stats,
                "series": series,
                "recent_batches": list(self._recent_batches)[:25],
                "cli_lines": list(self._cli_lines)[-100:],
                "audit": list(self._audit_log)[:60],
            }
