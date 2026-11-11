"""Cross-platform Browser Studio HTTP server for Linux, macOS, and Windows.

Uses Python's standard-library `ThreadingHTTPServer` so zero external web frameworks
are required, delegating 100% of operations to `CliSubprocessBridge` (CLI + JSON).
"""

from __future__ import annotations

import json
import mimetypes
import sys
import urllib.parse
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .cli_bridge import CliSubprocessBridge
from .locale_manager import LocaleManager, get_default_locale_manager

STATIC_DIR = Path(__file__).resolve().parent / "static"
if not STATIC_DIR.is_dir() and getattr(sys, "_MEIPASS", None):  # pragma: no cover
    _cand = Path(sys._MEIPASS) / "purpleair_data_logger" / "gui" / "static"
    if _cand.is_dir():
        STATIC_DIR = _cand
mimetypes.add_type("image/x-icon", ".ico")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/x-icns", ".icns")


class StudioHttpServer(ThreadingHTTPServer):
    """ThreadingHTTPServer carrying a shared CliSubprocessBridge instance."""

    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        bridge: CliSubprocessBridge,
        locale_mgr: LocaleManager | None = None,
    ) -> None:
        self.bridge = bridge
        self.locale_mgr = locale_mgr or get_default_locale_manager()
        super().__init__(server_address, StudioRequestHandler)


class StudioRequestHandler(BaseHTTPRequestHandler):
    """REST JSON + static asset handler backed strictly by CliSubprocessBridge."""

    server: StudioHttpServer

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return

    def _send_json(self, payload: Any, status: int = HTTPStatus.OK) -> None:
        body = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        data = json.loads(raw) if raw.strip() else {}
        if not isinstance(data, dict):
            raise ValueError("JSON request body must be an object")
        return data

    def _serve_static(self, rel_path: str) -> None:
        clean = rel_path.lstrip("/") or "index.html"
        target = (STATIC_DIR / clean).resolve()
        if (
            not str(target).startswith(str(STATIC_DIR.resolve()))
            or not target.is_file()
        ):
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        content = target.read_bytes()
        ctype, _ = mimetypes.guess_type(str(target))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        bridge = self.server.bridge

        try:
            if parsed.path == "/api/status":
                self._send_json({"ok": True, **bridge.snapshot()})
                return
            if parsed.path == "/api/locale":
                req_locale = qs.get("locale", [self.server.locale_mgr.locale])[0]
                self._send_json(
                    {
                        "ok": True,
                        "locale": req_locale,
                        "supported": self.server.locale_mgr.supported_locales(),
                        "strings": self.server.locale_mgr.get_locale_dict(req_locale),
                    }
                )
                return
            if parsed.path == "/api/config":
                self._send_json(
                    {
                        "ok": True,
                        "path": str(bridge.config_path),
                        "raw": bridge.load_config_text(),
                        "config": bridge.load_config_dict(),
                    }
                )
                return
            if parsed.path == "/api/version":
                self._send_json(bridge.version_info())
                return
            if parsed.path == "/api/schema":
                res = bridge.schema()
                schema_obj = (
                    json.loads(res["stdout"])
                    if res["ok"] and res["stdout"].strip()
                    else {}
                )
                self._send_json(
                    {"ok": res["ok"], "schema": schema_obj, "audit": res["audit"]}
                )
                return
            if parsed.path == "/api/template":
                tpl = qs.get("name", ["demo"])[0]
                res = bridge.init_config_template(tpl)
                self._send_json(
                    {
                        "ok": res["ok"],
                        "template": tpl,
                        "raw": res["stdout"],
                        "audit": res["audit"],
                    }
                )
                return
            if parsed.path == "/api/inspect":
                limit = int(qs.get("limit", ["50"])[0])
                dut = qs.get("dut", [""])[0]
                metric = qs.get("metric", [""])[0]
                self._send_json(bridge.inspect(limit=limit, dut=dut, metric=metric))
                return

            self._serve_static(parsed.path)
        except Exception as exc:
            self._send_json(
                {"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST
            )

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        bridge = self.server.bridge

        try:
            body = self._read_json_body()
            if parsed.path == "/api/config":
                if "raw" in body and isinstance(body["raw"], str):
                    res = bridge.save_config_text(body["raw"])
                elif "config" in body and isinstance(body["config"], dict):
                    res = bridge.save_config_dict(body["config"])
                else:
                    raise ValueError("Expected 'raw' string or 'config' object")
                self._send_json(res)
                return
            if parsed.path == "/api/validate":
                raw_cfg = body.get("raw") if isinstance(body.get("raw"), str) else None
                self._send_json(bridge.validate(config_text=raw_cfg))
                return
            if parsed.path == "/api/probe":
                self._send_json(bridge.probe(dut_name=str(body.get("dut", ""))))
                return
            if parsed.path == "/api/request":
                oids = body.get("oids", [])
                if isinstance(oids, str):
                    oids = [x.strip() for x in oids.split(",") if x.strip()]
                self._send_json(
                    bridge.request(
                        dut_name=str(body.get("dut", "")),
                        operation=str(body.get("operation", "get")),
                        oids=list(oids),
                        max_repeaters=int(body.get("max_repeaters", 10)),
                        record=bool(body.get("record", False)),
                    )
                )
                return
            if parsed.path == "/api/set":
                self._send_json(
                    bridge.set_oid(
                        dut_name=str(body.get("dut", "")),
                        oid=str(body.get("oid", "")),
                        set_type=str(body.get("set_type", "s")),
                        value=str(body.get("value", "")),
                        record=bool(body.get("record", False)),
                    )
                )
                return
            if parsed.path == "/api/run/start":
                self._send_json(bridge.start_run())
                return
            if parsed.path == "/api/run/stop":
                self._send_json(bridge.stop_run())
                return
            if parsed.path == "/api/run/once":
                self._send_json(bridge.run_once())
                return
            if parsed.path == "/api/locale":
                req_locale = str(body.get("locale", "")).strip()
                if req_locale:
                    self.server.locale_mgr.set_locale(req_locale)
                self._send_json(
                    {
                        "ok": True,
                        "locale": self.server.locale_mgr.locale,
                        "supported": self.server.locale_mgr.supported_locales(),
                        "strings": self.server.locale_mgr.get_locale_dict(
                            self.server.locale_mgr.locale
                        ),
                    }
                )
                return

            self._send_json(
                {"ok": False, "error": "Unknown API endpoint"},
                status=HTTPStatus.NOT_FOUND,
            )
        except Exception as exc:
            self._send_json(
                {"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST
            )


def create_web_server(
    bridge: CliSubprocessBridge,
    host: str = "127.0.0.1",
    port: int = 8765,
    locale_mgr: LocaleManager | None = None,
) -> StudioHttpServer:
    """Create a bound StudioHttpServer instance (supports port=0 ephemeral bind)."""
    return StudioHttpServer((host, port), bridge, locale_mgr=locale_mgr)


def launch_web_gui(
    bridge: CliSubprocessBridge,
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
    locale_mgr: LocaleManager | None = None,
) -> int:
    """Start the cross-platform Browser Studio and block until Ctrl+C."""
    srv = create_web_server(bridge, host=host, port=port, locale_mgr=locale_mgr)
    actual_host, actual_port = srv.server_address[:2]
    url = f"http://{actual_host}:{actual_port}/"  # NOSONAR
    print(f"PurpleAir Data Logger Browser Studio listening at {url}")
    print(f"JSON Configuration: {bridge.config_path}")
    print(f"Behind-the-scenes CLI: {' '.join(bridge.cli_base_command())}")

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Browser Studio and stopping CLI logger...")
    finally:
        bridge.stop_run()
        srv.server_close()
    return 0


__all__ = [
    "STATIC_DIR",
    "StudioHttpServer",
    "StudioRequestHandler",
    "create_web_server",
    "launch_web_gui",
]
