#!/usr/bin/env python3
"""
Copyright 2025 carlkidcrypto, All rights reserved.

Unit tests for PurpleAirMatterDataLogger.
"""

import http.client
import json
import os
import sys
import tempfile
import threading
import time
import unittest
import urllib.request
import urllib.error
from unittest.mock import Mock, patch

import requests_mock

sys.path.append("../")

from purpleair_data_logger.PurpleAirMatterDataLogger import (
    PurpleAirDataLoggerError,
    PurpleAirMatterDataLogger,
    _MatterHTTPServer,
    _MatterDataLoggerHandler,
    main,
)
from purpleair_data_logger.PurpleAirMatterDataLoggerConstants import (
    MATTER_DATA_LOGGER_DEFAULT_PORT,
    MATTER_DATA_LOGGER_DEFAULT_HOST,
    MATTER_ALL_SENSORS_PATH,
    MATTER_SENSOR_PATH_PREFIX,
    HEALTH_PATH,
)

# =============================================================================
# Fixtures
# =============================================================================

PA_SENSOR_PAYLOAD = {
    "sensor": {
        "sensor_index": 282168,
        "name": "Test Sensor",
        "pm2.5": 12.3,
        "pm10.0": 15.0,
        "pm1.0": 5.2,
        "voc": 0.3,
        "humidity": 55,
        "temperature": 72,
        "pressure": 14.7,
        "latitude": 37.7749,
        "longitude": -122.4194,
        "firmware_version": "7.0",
        "hardware": "PMS5003",
    }
}


# =============================================================================
# Tests — Constructor
# =============================================================================


class PurpleAirMatterDataLoggerConstructorTest(unittest.TestCase):
    """Tests for PurpleAirMatterDataLogger.__init__."""

    def test_default_port(self):
        """Default HTTP port is MATTER_DATA_LOGGER_DEFAULT_PORT."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
        self.assertEqual(logger._http_port, MATTER_DATA_LOGGER_DEFAULT_PORT)

    def test_default_host(self):
        """Default HTTP host is MATTER_DATA_LOGGER_DEFAULT_HOST."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
        self.assertEqual(logger._http_host, MATTER_DATA_LOGGER_DEFAULT_HOST)

    def test_matter_only_default_false(self):
        """matter_only defaults to False."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
        self.assertFalse(logger._matter_only)

    def test_custom_port_and_host(self):
        """Custom port and host are accepted."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(
                PurpleAirApiReadKey="test",
                http_port=9876,
                http_host="127.0.0.1",
            )
        self.assertEqual(logger._http_port, 9876)
        self.assertEqual(logger._http_host, "127.0.0.1")

    def test_poll_interval_minimum_enforced(self):
        """poll_interval_seconds below 60 is clamped to 60."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(
                PurpleAirApiReadKey="test",
                poll_interval_seconds=10,
            )
        self.assertEqual(logger._poll_interval, 60)

    def test_start_http_server_starts_thread_and_serves(self):
        """_start_http_server spins up a live HTTP server on a background thread."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(
                PurpleAirApiReadKey="test",
                http_port=0,
                http_host="127.0.0.1",
            )
        try:
            logger._start_http_server()
            self.assertIsNotNone(logger._httpd)
            self.assertIsInstance(logger._http_thread, threading.Thread)
            self.assertTrue(logger._http_thread.is_alive())

            actual_port = logger._httpd.server_address[1]
            conn = http.client.HTTPConnection("127.0.0.1", actual_port, timeout=5)
            conn.request("GET", HEALTH_PATH)
            resp = conn.getresponse()
            resp.read()
            conn.close()
            self.assertEqual(resp.status, 200)
        finally:
            if logger._httpd is not None:
                logger._httpd.shutdown()
                logger._httpd.server_close()
            if logger._http_thread is not None:
                logger._http_thread.join(timeout=5)


# =============================================================================
# Tests — One-shot conversion
# =============================================================================


class PurpleAirMatterDataLoggerRunOnceTest(unittest.TestCase):
    """Tests for PurpleAirMatterDataLogger.run_once."""

    def test_run_once_returns_matter_device(self):
        """run_once returns a dict mapping sensor_index → Matter device dict."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.purpleair.com/v1/keys",
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            m.get(
                "https://api.purpleair.com/v1/sensors/282168",
                json={"sensor": PA_SENSOR_PAYLOAD["sensor"]},
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
            result = logger.run_once([282168])

        self.assertIn(282168, result)
        device = result[282168]
        self.assertEqual(device["device_type"]["id"], 0x002D)
        self.assertIn("clusters", device)
        self.assertIn("air_quality_measurement", device["clusters"])

    def test_run_once_multiple_sensors(self):
        """run_once converts multiple sensors."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            sensor_a = dict(PA_SENSOR_PAYLOAD["sensor"], sensor_index=111111, name="A")
            sensor_b = dict(PA_SENSOR_PAYLOAD["sensor"], sensor_index=222222, name="B")
            m.get(
                "https://api.purpleair.com/v1/sensors/111111",
                json={"sensor": sensor_a},
                status_code=200,
            )
            m.get(
                "https://api.purpleair.com/v1/sensors/222222",
                json={"sensor": sensor_b},
                status_code=200,
            )

            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
            result = logger.run_once([111111, 222222])

        self.assertEqual(len(result), 2)
        self.assertIn(111111, result)
        self.assertIn(222222, result)

    def test_run_once_unknown_sensor(self):
        """run_once returns an empty dict when no sensors are found."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
            result = logger.run_once([])

        self.assertEqual(result, {})


# =============================================================================
# Tests — HTTP Server endpoints
# =============================================================================


class MatterHTTPServerEndpointsTest(unittest.TestCase):
    """Tests for the embedded HTTP server endpoints."""

    @classmethod
    def setUpClass(cls):
        # Shared device map and server shared across all test methods
        cls.devices: dict[int, dict] = {
            282168: {
                "device_type": {
                    "id": 0x002D,
                    "label": "Air Quality Sensor",
                    "matter_version": "1.5.1",
                },
                "clusters": {"air_quality_measurement": {"cluster_id": 0x005D}},
            }
        }
        cls.httpd = _MatterHTTPServer(
            server_address=("127.0.0.1", 0),
            RequestHandlerClass=_MatterDataLoggerHandler,
            matter_devices=cls.devices,
            lock=threading.Lock(),
        )
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)

    def _get(self, path: str) -> tuple[int, dict]:
        """Make a GET request and return (status_code, json_body)."""
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{self.port}{path}", timeout=2
            ) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def test_health_endpoint_returns_200(self):
        """GET /health returns 200."""
        status, body = self._get(HEALTH_PATH)
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["sensor_count"], 1)

    def test_endpoints_accept_query_parameters(self):
        """Query parameters do not interfere with endpoint routing."""
        health_status, _ = self._get(f"{HEALTH_PATH}?probe=true")
        sensor_status, _ = self._get(f"{MATTER_SENSOR_PATH_PREFIX}/282168?precision=2")
        self.assertEqual(health_status, 200)
        self.assertEqual(sensor_status, 200)

    def test_server_reuses_address(self):
        """The HTTP server allows quick restarts on the same address."""
        self.assertTrue(_MatterHTTPServer.allow_reuse_address)

    def test_health_root_endpoint_returns_200(self):
        """GET / returns 200 (redirects to health)."""
        status, body = self._get("/")
        self.assertEqual(status, 200)

    def test_all_sensors_endpoint(self):
        """GET /matter/sensors returns all devices."""
        status, body = self._get(MATTER_ALL_SENSORS_PATH)
        self.assertEqual(status, 200)
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["sensors"][0]["sensor_index"], 282168)
        self.assertIn("_status", body["sensors"][0])
        self.assertIn("_last_seen", body["sensors"][0])

    def test_single_sensor_endpoint(self):
        """GET /matter/sensor/<id> returns that sensor's device."""
        status, body = self._get(f"{MATTER_SENSOR_PATH_PREFIX}/282168")
        self.assertEqual(status, 200)
        self.assertEqual(body["device"]["device_type"]["id"], 0x002D)
        self.assertIn("_status", body)
        self.assertIn("_last_seen", body)

    def test_single_sensor_not_found(self):
        """GET /matter/sensor/<unknown> returns 404."""
        status, body = self._get(f"{MATTER_SENSOR_PATH_PREFIX}/999999")
        self.assertEqual(status, 404)
        self.assertIn("error", body)

    def test_single_sensor_invalid_id(self):
        """GET /matter/sensor/<non-int> returns 400."""
        status, body = self._get(f"{MATTER_SENSOR_PATH_PREFIX}/abc")
        self.assertEqual(status, 400)

    def test_unknown_path_returns_404(self):
        """Unknown paths return 404."""
        status, _ = self._get("/nonexistent")
        self.assertEqual(status, 404)

    def test_head_request_returns_204(self):
        """HEAD requests return 204 with a Content-Type header."""
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        try:
            conn.request("HEAD", HEALTH_PATH)
            resp = conn.getresponse()
            self.assertEqual(resp.status, 204)
            self.assertEqual(
                resp.getheader("Content-Type"), "application/json; charset=utf-8"
            )
        finally:
            conn.close()


# =============================================================================
# Tests — Config file validation
# =============================================================================


class PurpleAirMatterDataLoggerConfigTest(unittest.TestCase):
    """Tests for config file loading in validate_parameters_and_run."""

    def test_validate_uses_constructor_defaults_without_config(self):
        """Constructor sensor defaults are used when no config file is passed."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(
                PurpleAirApiReadKey="test",
                sensor_indexes=[282168],
                sensor_names={282168: "Default Name"},
                read_keys={282168: "sensor-read-key"},
            )
            started = {"value": False}
            received_config = {"value": None}

            logger._start_http_server = lambda: started.__setitem__("value", True)
            logger._run_loop_matter = lambda config: received_config.__setitem__(
                "value", config
            )

            logger.validate_parameters_and_run()

        self.assertTrue(started["value"])
        self.assertEqual(received_config["value"], {})

    def test_validate_rejects_multiple_config_files(self):
        """Providing more than one config file raises PurpleAirDataLoggerError."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
            f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
            try:
                json.dump({"poll_interval_seconds": 65, "sensor_indexes": [1]}, f)
                f.flush()
                with self.assertRaises(PurpleAirDataLoggerError) as ctx:
                    logger.validate_parameters_and_run(
                        paa_multiple_sensor_request_json_file=f.name,
                        paa_single_sensor_request_json_file=f.name,
                    )
                self.assertIn("Only one config", str(ctx.exception))
            finally:
                f.close()
                os.unlink(f.name)

    def test_validate_loads_settings_from_config_file(self):
        """A valid config file overrides constructor defaults."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
            f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
            try:
                json.dump(
                    {
                        "poll_interval_seconds": 120,
                        "http_port": 9999,
                        "http_host": "0.0.0.0",
                        "matter_only": True,
                        "sensor_indexes": [282168],
                    },
                    f,
                )
                f.flush()

                started = {"value": False}
                received_config = {"value": None}
                logger._start_http_server = lambda: started.__setitem__("value", True)
                logger._run_loop_matter = lambda config: received_config.__setitem__(
                    "value", config
                )

                logger.validate_parameters_and_run(
                    paa_multiple_sensor_request_json_file=f.name,
                )
            finally:
                f.close()
                os.unlink(f.name)

        self.assertTrue(started["value"])
        self.assertEqual(logger._poll_interval, 120)
        self.assertEqual(logger._http_port, 9999)
        self.assertEqual(logger._http_host, "0.0.0.0")
        self.assertTrue(logger._matter_only)
        self.assertEqual(received_config["value"]["sensor_indexes"], [282168])

    def test_validate_raises_without_sensors_or_ip_list(self):
        """No sensor_indexes and no sensor_ip_list raises PurpleAirDataLoggerError."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")

            with self.assertRaises(PurpleAirDataLoggerError) as ctx:
                logger.validate_parameters_and_run()
            self.assertIn("nothing to poll", str(ctx.exception))

    def test_matter_only_flag_overrides_constructor(self):
        """The matter_only kwarg overrides the constructor's stored value."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(
                PurpleAirApiReadKey="test", sensor_indexes=[282168]
            )
            logger._start_http_server = lambda: None
            logger._run_loop_matter = lambda config: None

            logger.validate_parameters_and_run(matter_only=True)

        self.assertTrue(logger._matter_only)

    def test_validate_succeeds_with_constructor_ipv4_address_list(self):
        """Constructor-provided PurpleAirApiIpv4Address list satisfies validation."""
        logger = PurpleAirMatterDataLogger(PurpleAirApiIpv4Address=["192.168.1.50"])
        started = {"value": False}
        logger._start_http_server = lambda: started.__setitem__("value", True)
        logger._run_loop_matter = lambda config: None

        logger.validate_parameters_and_run()
        self.assertTrue(started["value"])

    def test_validate_succeeds_with_constructor_ipv4_address_string(self):
        """Constructor-provided single string PurpleAirApiIpv4Address satisfies validation."""
        logger = PurpleAirMatterDataLogger(PurpleAirApiIpv4Address="192.168.1.50")
        self.assertEqual(logger._sensor_ip_list, ["192.168.1.50"])
        started = {"value": False}
        logger._start_http_server = lambda: started.__setitem__("value", True)
        logger._run_loop_matter = lambda config: None

        logger.validate_parameters_and_run()
        self.assertTrue(started["value"])


class MainCliTest(unittest.TestCase):
    """Tests for the main() CLI entry point."""

    def test_main_invokes_validate_parameters_and_run(self):
        """main() constructs a logger from CLI args and runs it."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            with patch(
                "purpleair_data_logger.PurpleAirMatterDataLogger."
                "PurpleAirMatterDataLogger.validate_parameters_and_run"
            ) as mock_run:
                main(
                    [
                        "-paa_read_key",
                        "test",
                        "--http-port",
                        "9877",
                        "--matter-only",
                    ]
                )
        mock_run.assert_called_once()

    def test_main_loads_local_config_ip_list(self):
        """main() reads sensor_ip_list from the local sensor config file."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
            try:
                json.dump({"sensor_ip_list": ["192.168.1.100"]}, f)
                f.flush()

                with patch(
                    "purpleair_data_logger.PurpleAirMatterDataLogger."
                    "PurpleAirMatterDataLogger.validate_parameters_and_run"
                ) as mock_run:
                    main(
                        [
                            "-paa_read_key",
                            "test",
                            "-paa_local_sensor_request_json_file",
                            f.name,
                        ]
                    )
                mock_run.assert_called_once()
            finally:
                f.close()
                os.unlink(f.name)

    def test_main_warns_on_save_file_path(self):
        """main() logs a warning and proceeds when -save_file_path is given."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            with patch(
                "purpleair_data_logger.PurpleAirMatterDataLogger."
                "PurpleAirMatterDataLogger.validate_parameters_and_run"
            ) as mock_run:
                main(
                    [
                        "-paa_read_key",
                        "test",
                        "-save_file_path",
                        "/tmp/unused.csv",
                    ]
                )
        mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
