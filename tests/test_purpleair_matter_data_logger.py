#!/usr/bin/env python3
"""
Copyright 2025 carlkidcrypto, All rights reserved.

Unit tests for PurpleAirMatterDataLogger.
"""

import json
import sys
import os
import tempfile
import threading
import unittest
import urllib.request
import urllib.error

import requests_mock

sys.path.append("../")

from purpleair_data_logger.PurpleAirMatterDataLogger import (
    PurpleAirDataLoggerError,
    PurpleAirMatterDataLogger,
    _MatterHTTPServer,
    _MatterDataLoggerHandler,
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

    def test_single_sensor_endpoint(self):
        """GET /matter/sensor/<id> returns that sensor's device."""
        status, body = self._get(f"{MATTER_SENSOR_PATH_PREFIX}/282168")
        self.assertEqual(status, 200)
        self.assertEqual(body["device"]["device_type"]["id"], 0x002D)

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


# =============================================================================
# Tests — Matter device type correctness
# =============================================================================


class MatterDeviceTypeCorrectnessTest(unittest.TestCase):
    """Integration tests to verify Matter device type compliance."""

    def test_air_quality_sensor_device_type_id(self):
        """Device type id is 0x002D (Air Quality Sensor)."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            m.get(
                "https://api.purpleair.com/v1/sensors/282168",
                json=PA_SENSOR_PAYLOAD,
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
            result = logger.run_once([282168])

        device = result[282168]
        self.assertEqual(device["device_type"]["id"], 0x002D)
        self.assertEqual(device["device_type"]["matter_version"], "1.5.1")

    def test_air_quality_clusters_present(self):
        """Air Quality, Temperature, Humidity, and Pressure clusters are present."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            m.get(
                "https://api.purpleair.com/v1/sensors/282168",
                json=PA_SENSOR_PAYLOAD,
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
            result = logger.run_once([282168])

        clusters = result[282168]["clusters"]
        self.assertIn("air_quality_measurement", clusters)
        self.assertIn("temperature_measurement", clusters)
        self.assertIn("humidity_measurement", clusters)
        self.assertIn("pressure_measurement", clusters)

    def test_sensor_name_override_applied(self):
        """sensor_names in run_once overrides the PurpleAir name."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            m.get(
                "https://api.purpleair.com/v1/sensors/282168",
                json=PA_SENSOR_PAYLOAD,
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
            result = logger.run_once(
                [282168],
                sensor_names={282168: "My Custom Name"},
            )

        self.assertEqual(result[282168]["sensor_name"], "My Custom Name")

    def test_epa_aqi_computed_in_output(self):
        """EPA AQI is present in the air quality summary."""
        with requests_mock.Mocker() as m:
            m.get(
                requests_mock.ANY,
                text='{"api_version": "1.1.1", "time_stamp": 0, "api_key_type": "READ"}',
                status_code=200,
            )
            m.get(
                "https://api.purpleair.com/v1/sensors/282168",
                json=PA_SENSOR_PAYLOAD,
                status_code=200,
            )
            logger = PurpleAirMatterDataLogger(PurpleAirApiReadKey="test")
            result = logger.run_once([282168])

        summary = result[282168]["air_quality_summary"]
        self.assertIn("epa_aqi", summary)
        self.assertIsInstance(summary["epa_aqi"], int)
        self.assertGreaterEqual(summary["epa_aqi"], 0)


if __name__ == "__main__":
    unittest.main()
