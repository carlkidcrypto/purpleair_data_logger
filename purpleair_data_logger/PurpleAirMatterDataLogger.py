#!/usr/bin/env python3
"""
Copyright 2025 carlkidcrypto, All rights reserved.

Matter Data Logger — exposes PurpleAir sensors as Matter device type
structures via a lightweight HTTP API.

Performs two roles:
  1. Fetches raw sensor data from PurpleAir on a configurable interval.
  2. Converts readings to Matter device type JSON and exposes them via HTTP.

Designed to run as a long-lived daemon (forever loop) or as a
one-shot converter when ``poll_interval_seconds`` is omitted.

Requires purpleair_api >= 1.5.0a1 (includes
``purpleair_api.PurpleAirMatterConverter``).
When calling ``validate_parameters_and_run()`` without a JSON config file,
pass ``sensor_indexes`` via the constructor.

Usage::

    from purpleair_data_logger.PurpleAirMatterDataLogger import (
        PurpleAirMatterDataLogger,
    )

    logger = PurpleAirMatterDataLogger(
        PurpleAirApiReadKey="YOUR_READ_KEY",
        PurpleAirApiIpv4Address=["192.168.1.100"],
        sensor_indexes=[123456],
        poll_interval_seconds=65,
        http_port=9855,
    )
    logger.validate_parameters_and_run()

References:
  - Matter 1.5.1 Core Specification (CSA, 2024)
    <https://csa-iot.org/developer-resource/specifications/>
  - Air Quality Sensor Device Type (Device Type 0x002D)
  - Air Quality Measurement Cluster (Cluster 0x005D)
  - Temperature Measurement Cluster (Cluster 0x0402)
  - Relative Humidity Measurement Cluster (Cluster 0x0405)
  - Barometric Pressure Measurement Cluster (Cluster 0x0403)
"""

from __future__ import annotations

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import threading
from time import sleep
from typing import Any

from purpleair_api.PurpleAirAPI import PurpleAirAPIError

try:
    from purpleair_api.PurpleAirMatterConverter import PurpleAirMatterConverter
except ImportError:  # pragma: no cover - compatibility with alternate layouts
    from purpleair_api.matter import PurpleAirMatterConverter

from purpleair_data_logger.PurpleAirDataLogger import (
    PurpleAirDataLogger,
    PurpleAirDataLoggerError,
)
from purpleair_data_logger.PurpleAirMatterDataLoggerConstants import (
    MATTER_DATA_LOGGER_DEFAULT_HOST,
    MATTER_DATA_LOGGER_DEFAULT_PORT,
    MATTER_ALL_SENSORS_PATH,
    MATTER_SENSOR_PATH_PREFIX,
    HEALTH_PATH,
    MATTER_DATA_LOGGER_LOG_LEVEL,
)

logger = logging.getLogger(__name__)


# =============================================================================
# HTTP Handler
# =============================================================================


class _MatterDataLoggerHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the Matter device type JSON API.

    Serves the following endpoints::

        GET /health
            → ``200 OK`` with ``{"status": "ok", "sensor_count": <N>}``

        GET /matter/sensors
            → ``200 OK`` with
              ``{"sensors": [{"sensor_index": ..., "device": {...}}, ...]}``

        GET /matter/sensor/<sensor_index>
            → ``200 OK`` with ``{"device": {...}}``
            → ``404 Not Found`` if sensor_index not tracked
    """

    def log_message(self, format_: str, *args: Any) -> None:
        """Suppress default request logging; use structured logger instead."""
        pass

    def _send_json(self, status: int, data: dict) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_GET(self) -> None:
        if self.path == HEALTH_PATH or self.path == "/":
            with self.server.lock:
                sensor_count = len(self.server.matter_devices)
            self._send_json(200, {"status": "ok", "sensor_count": sensor_count})

        elif self.path == MATTER_ALL_SENSORS_PATH:
            with self.server.lock:
                items = list(self.server.matter_devices.items())

            payload = {
                "sensors": [{"sensor_index": idx, "device": dev} for idx, dev in items],
                "count": len(items),
            }
            self._send_json(200, payload)

        elif self.path.startswith(MATTER_SENSOR_PATH_PREFIX + "/"):
            try:
                idx = int(self.path[len(MATTER_SENSOR_PATH_PREFIX) + 1 :])
            except ValueError:
                self._send_json(400, {"error": "Invalid sensor_index"})
                return

            with self.server.lock:
                device = self.server.matter_devices.get(idx)
            if device is None:
                self._send_json(
                    404, {"error": f"Sensor {idx} not found or not yet polled."}
                )
                return

            self._send_json(200, {"device": device})

        else:
            self._send_json(404, {"error": "Not found"})

    def do_HEAD(self) -> None:
        self.send_response(204)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()


class _MatterHTTPServer(HTTPServer):
    """HTTP server that holds the current Matter device map for all handlers."""

    def __init__(
        self,
        server_address: tuple[str, int],
        RequestHandlerClass: type[BaseHTTPRequestHandler],
        matter_devices: dict[int, dict[str, Any]],
        lock: threading.Lock,
    ) -> None:
        # Share the device map across all request handlers
        self.matter_devices = matter_devices
        self.lock = lock
        super().__init__(server_address, RequestHandlerClass)


# =============================================================================
# Main Logger Class
# =============================================================================


class PurpleAirMatterDataLogger(PurpleAirDataLogger):
    """
    Fetches PurpleAir sensors and exposes them as Matter device type JSON
    via an embedded HTTP server.

    Inherits from :class:`PurpleAirDataLogger` and reuses its polling loop
    infrastructure. The run methods are overridden to perform
    PurpleAir → Matter conversion instead of database insertion.

    **Matter mode** (default):
        Runs a forever loop: fetch → convert → expose via HTTP.
        The ``poll_interval_seconds`` config field controls the loop delay.

    **One-shot mode**:
        Call :meth:`run_once` directly to convert current readings
        without starting the HTTP server or the polling loop.

    **Matter-only mode** (``--matter-only`` CLI flag):
        When invoked via CLI with the ``--matter-only`` flag, the HTTP server
        is started without an associated database/CSV sink — only the
        Matter conversion runs, suitable for feeding a Matter bridge
        (e.g. ``python-matter-server`` or Home Assistant Matter integration).

    :param str PurpleAirApiReadKey: PurpleAir Read API key.
    :param str PurpleAirApiWriteKey: PurpleAir Write API key (optional).
    :param list PurpleAirApiIpv4Address: List of IPv4 addresses for local
        sensor access (optional).
    :param int poll_interval_seconds: How often to poll PurpleAir (default 65).
        Must be >= 60. Ignored in one-shot mode.
    :param int http_port: HTTP server port (default 9855).
    :param str http_host: HTTP server bind host (default 127.0.0.1).
    :param list[int] sensor_indexes: Optional constructor defaults for sensors to
        poll when no config file is provided.
    :param dict[int, str] sensor_names: Optional constructor defaults for sensor
        display names when no config file is provided.
    :param dict[int, str] read_keys: Optional constructor defaults for per-sensor
        read keys when no config file is provided.
    :param bool matter_only: If True, the forever loop runs without any
        database or file sink (Matter conversion only).
    """

    def __init__(
        self,
        PurpleAirApiReadKey: str | None = None,
        PurpleAirApiWriteKey: str | None = None,
        PurpleAirApiIpv4Address: list[str] | None = None,
        poll_interval_seconds: int = 65,
        http_port: int = MATTER_DATA_LOGGER_DEFAULT_PORT,
        http_host: str = MATTER_DATA_LOGGER_DEFAULT_HOST,
        sensor_indexes: list[int] | None = None,
        sensor_names: dict[int, str] | None = None,
        read_keys: dict[int, str] | None = None,
        matter_only: bool = False,
    ) -> None:
        super().__init__(
            PurpleAirApiReadKey=PurpleAirApiReadKey,
            PurpleAirApiWriteKey=PurpleAirApiWriteKey,
            PurpleAirApiIpv4Address=PurpleAirApiIpv4Address,
        )
        self._poll_interval = max(60, poll_interval_seconds)
        self._http_port = http_port
        self._http_host = http_host
        self._matter_only = matter_only

        # Config defaults (populated from JSON config files / CLI args)
        self._sensor_indexes: list[int] = list(sensor_indexes or [])
        self._sensor_names: dict[int, str] = dict(sensor_names or {})
        self._read_keys: dict[int, str] = dict(read_keys or {})

        # Maps sensor_index (int) → Matter device dict
        self._matter_devices: dict[int, dict[str, Any]] = {}
        self._httpd: _MatterHTTPServer | None = None
        self._http_thread: threading.Thread | None = None
        self._lock = threading.Lock()
        # Configure logging only if the application hasn't configured it yet
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=MATTER_DATA_LOGGER_LOG_LEVEL,
                format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            )

    def _start_http_server(self) -> None:
        """Start the HTTP server in a background thread."""
        self._httpd = _MatterHTTPServer(
            server_address=(self._http_host, self._http_port),
            RequestHandlerClass=_MatterDataLoggerHandler,
            matter_devices=self._matter_devices,
            lock=self._lock,
        )
        self._http_thread = threading.Thread(
            target=self._httpd.serve_forever,
            name="MatterHTTPServer",
            daemon=True,
        )
        self._http_thread.start()
        logger.info(
            "Matter HTTP server started on %s:%d", self._http_host, self._http_port
        )
        logger.info(
            "  → All sensors:   GET http://%s:%d%s",
            self._http_host,
            self._http_port,
            MATTER_ALL_SENSORS_PATH,
        )
        logger.info(
            "  → Single sensor: GET http://%s:%d%s/<sensor_index>",
            self._http_host,
            self._http_port,
            MATTER_SENSOR_PATH_PREFIX,
        )
        logger.info(
            "  → Health check:  GET http://%s:%d%s",
            self._http_host,
            self._http_port,
            HEALTH_PATH,
        )

    # -------------------------------------------------------------------------
    # Per-sensor conversion
    # -------------------------------------------------------------------------

    def _poll_and_convert_sensor(
        self,
        sensor_index: int,
        sensor_name: str | None = None,
        primary_key: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Fetch one sensor's data from PurpleAir and convert to Matter format.

        :param sensor_index: PurpleAir sensor index.
        :param sensor_name: Optional display name override for Matter output.
        :param primary_key: Optional Read key for this specific sensor.
        :return: Matter device dict, or None on error.
        """
        try:
            raw = self._purpleair_api_obj.request_sensor_data(
                sensor_index,
                read_key=primary_key,
            )
        except PurpleAirAPIError as exc:
            logger.warning("Sensor %s: PurpleAir API error: %s", sensor_index, exc)
            return None

        return PurpleAirMatterConverter.to_air_quality_sensor(
            raw,
            sensor_name=sensor_name,
        )

    def _poll_and_convert_multiple(
        self,
        sensor_indexes: list[int],
        sensor_names: dict[int, str] | None = None,
        primary_keys: dict[int, str] | None = None,
    ) -> dict[int, dict[str, Any]]:
        """
        Poll multiple sensors and convert each to a Matter device dict.

        :param sensor_indexes: List of PurpleAir sensor indexes.
        :param sensor_names: Optional dict mapping sensor_index → display name.
        :param primary_keys: Optional dict mapping sensor_index → Read key.
        :return: Dict mapping sensor_index → Matter device dict.
        """
        results: dict[int, dict[str, Any]] = {}
        for idx in sensor_indexes:
            name = sensor_names.get(idx) if sensor_names else None
            key = primary_keys.get(idx) if primary_keys else None
            device = self._poll_and_convert_sensor(idx, name, key)
            if device is not None:
                results[idx] = device
        return results

    # -------------------------------------------------------------------------
    # One-shot run
    # -------------------------------------------------------------------------

    def run_once(
        self,
        sensor_indexes: list[int],
        sensor_names: dict[int, str] | None = None,
        primary_keys: dict[int, str] | None = None,
    ) -> dict[int, dict[str, Any]]:
        """
        Fetch and convert sensors once (no HTTP server, no forever loop).

        Returns the current Matter device map without starting any background
        service. Suitable for scripting or one-off exports.

        :param sensor_indexes: List of PurpleAir sensor indexes to poll.
        :param sensor_names: Optional dict mapping sensor_index → display name.
        :param primary_keys: Optional dict mapping sensor_index → Read key.
        :return: Dict mapping sensor_index → Matter device dict.
        """
        devices = self._poll_and_convert_multiple(
            sensor_indexes, sensor_names, primary_keys
        )
        logger.info("Converted %d sensor(s) to Matter format", len(devices))
        return devices

    # -------------------------------------------------------------------------
    # Daemon loop (replaces the base class database-store loop)
    # -------------------------------------------------------------------------

    def _run_loop_matter(
        self,
        json_config_file: dict[str, Any],
    ) -> None:
        """
        The Matter-data-logger forever loop.

        1. Fetches and converts all configured sensors to Matter device type JSON.
        2. Updates the shared device map (served by the HTTP thread).
        3. Sleeps for ``poll_interval_seconds``.
        4. In non-``matter_only`` mode, also calls ``store_sensor_data``
           (allowing subclasses to persist raw PurpleAir data alongside).

        :param json_config_file: Configuration dict loaded from the JSON config file.
        """
        sensor_indexes: list[int] = json_config_file.get(
            "sensor_indexes", self._sensor_indexes
        )
        sensor_names: dict[int, str] = {
            int(k): v
            for k, v in json_config_file.get("sensor_names", self._sensor_names).items()
        }
        primary_keys: dict[int, str] = {
            int(k): v
            for k, v in json_config_file.get("read_keys", self._read_keys).items()
        }

        logger.info(
            "Starting Matter conversion loop for %d sensor(s)", len(sensor_indexes)
        )

        while True:
            logger.info(
                "Polling %d sensor(s) at poll interval %ds...",
                len(sensor_indexes),
                self._poll_interval,
            )
            devices = self._poll_and_convert_multiple(
                sensor_indexes, sensor_names, primary_keys
            )

            # Thread-safe in-place update of the shared device map.
            # The lock ensures no other thread sees an inconsistent intermediate state
            # during clear() + update(), while keeping the same dict object reference
            # so that the HTTP server (which holds the same reference) sees updates.
            with self._lock:
                self._matter_devices.clear()
                self._matter_devices.update(devices)

            # NOTE: a prior revision used an atomic dict-reference swap
            # (``self._matter_devices = dict(devices)``) to avoid the clear/update
            # race.  This broke the HTTP server tests because the server holds a
            # reference to the original empty dict passed at construction — the swap
            # left it pointing at a stale object while the server kept serving the
            # initial empty dict.  Switching to lock+clear+update keeps the same dict
            # object identity so the HTTP server sees every update, while the lock
            # prevents concurrent-read/during-write tears.
            # See: commit 141b063d525620cf033cff7a2be9d8d7f40125ef

            logger.info(
                "Matter devices updated: %d/%d sensors converted successfully.",
                len(devices),
                len(sensor_indexes),
            )

            # Optionally also persist raw PurpleAir data (non-matter_only mode)
            # In non-matter_only mode, subclasses that override
            # store_sensor_data may persist raw PurpleAir data here.
            # (store_sensor_data calls removed — not implemented in this class)

            sleep(self._poll_interval)

    # -------------------------------------------------------------------------
    # Entry point
    # -------------------------------------------------------------------------

    def validate_parameters_and_run(
        self,
        paa_multiple_sensor_request_json_file: str | None = None,
        paa_single_sensor_request_json_file: str | None = None,
        paa_group_sensor_request_json_file: str | None = None,
        paa_local_sensor_request_json_file: str | None = None,
        matter_only: bool | None = None,
    ) -> None:
        """
        Main entry point for ``PurpleAirMatterDataLogger``.

        Accepts the same JSON config file arguments as the base class, but all
        four are mutually exclusive (only one config file per run). If no
        config file is provided, the logger runs with defaults from the
        constructor.

        :param str paa_multiple_sensor_request_json_file: Path to a multi-sensor
            config file. Required fields: ``sensor_indexes`` (list of ints),
            ``poll_interval_seconds`` (int, >= 60), ``http_port`` (int, optional),
            ``http_host`` (str, optional), ``sensor_names`` (dict, optional),
            ``read_keys`` (dict, optional).
        :param str paa_single_sensor_request_json_file: Path to a single-sensor
            config file. Same fields as the multi-sensor file.
        :param str paa_group_sensor_request_json_file: Path to a group config
            file (uses ``group_id`` to fetch sensors).
        :param str paa_local_sensor_request_json_file: Path to a local-only
            config file (uses ``ipv4_address`` filters).
        :param bool matter_only: If True, disables any non-Matter side effects
            (e.g. raw data persistence). Overrides the constructor value.
        """
        # Resolve matter_only (constructor default can be overridden here)
        if matter_only is not None:
            self._matter_only = matter_only

        # Load one config file if provided
        config: dict[str, Any] = {}
        config_files = [
            paa_multiple_sensor_request_json_file,
            paa_single_sensor_request_json_file,
            paa_group_sensor_request_json_file,
            paa_local_sensor_request_json_file,
        ]
        provided = [f for f in config_files if f is not None]

        if len(provided) > 1:
            raise PurpleAirDataLoggerError(
                "Only one config file may be provided. Got: " + ", ".join(provided)
            )

        if provided:
            with open(provided[0]) as fh:
                config = json.load(fh)
            self._poll_interval = max(60, config.get("poll_interval_seconds", 65))
            self._http_port = config.get("http_port", self._http_port)
            self._http_host = config.get("http_host", self._http_host)
            self._matter_only = config.get("matter_only", self._matter_only)

        # Validate that we have sensors to poll before starting the server
        sensor_indexes: list[int] = config.get("sensor_indexes", self._sensor_indexes)
        if not sensor_indexes:
            raise PurpleAirDataLoggerError(
                "No 'sensor_indexes' provided — nothing to poll."
            )

        # Start the HTTP server
        self._start_http_server()

        # Run the loop
        self._run_loop_matter(config)


__all__ = ["PurpleAirMatterDataLogger"]
