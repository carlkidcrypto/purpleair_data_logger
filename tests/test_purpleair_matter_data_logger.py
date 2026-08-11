#!/usr/bin/env python3
"""
Copyright 2025 carlkidcrypto, All rights reserved.

Unit tests for PurpleAirMatterDataLogger.
"""

import http.client
import json
import sys
import os
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from unittest.mock import Mock, patch

import requests_mock

sys.path.append("../")

from purpleair_api.PurpleAirAPI import PurpleAirAPIError
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


class PurpleAirMatterDataLoggerResilienceTest(unittest.TestCase):
    """Tests for failures encountered by the long-running polling loop."""

    def test_unexpected_sensor_error_is_isolated(self):
        """An unexpected client exception does not escape the sensor poll."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_sensor_data.side_effect = TimeoutError

        self.assertIsNone(logger._poll_and_convert_sensor(282168))

    def test_purpleair_api_error_is_isolated(self):
        """A PurpleAirAPIError does not escape the sensor poll."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_sensor_data.side_effect = PurpleAirAPIError(
            "boom"
        )

        self.assertIsNone(logger._poll_and_convert_sensor(282168))


class LocalAverageTest(unittest.TestCase):
    """Tests for PurpleAirMatterDataLogger._local_average."""

    def test_averages_both_channels(self):
        """Returns the mean of primary and secondary when both are present."""
        raw = {"pm2_5_atm": 10.0, "pm2_5_atm_b": 20.0}
        result = PurpleAirMatterDataLogger._local_average(
            raw, "pm2_5_atm", "pm2_5_atm_b"
        )
        self.assertEqual(result, 15.0)

    def test_returns_primary_when_secondary_missing(self):
        """Returns the primary value unmodified when secondary is absent."""
        raw = {"pm2_5_atm": 10.0}
        result = PurpleAirMatterDataLogger._local_average(
            raw, "pm2_5_atm", "pm2_5_atm_b"
        )
        self.assertEqual(result, 10.0)

    def test_returns_none_when_primary_missing(self):
        """Returns None when the primary reading itself is absent."""
        raw = {"pm2_5_atm_b": 20.0}
        result = PurpleAirMatterDataLogger._local_average(
            raw, "pm2_5_atm", "pm2_5_atm_b"
        )
        self.assertIsNone(result)


class PollAndConvertLocalTest(unittest.TestCase):
    """Tests for PurpleAirMatterDataLogger._poll_and_convert_local."""

    def test_api_error_returns_empty_dict(self):
        """A PurpleAirAPIError while polling local sensors yields {}."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_local_sensor_data.side_effect = (
            PurpleAirAPIError("local fail")
        )

        self.assertEqual(logger._poll_and_convert_local(), {})

    def test_converts_local_sensor_payload(self):
        """A valid local sensor payload is converted to a Matter device dict."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_local_sensor_data.return_value = {
            "192.168.1.50": {
                "SensorId": "aa:bb:cc:dd:ee:ff",
                "hardwarediscovered": "PMS5003",
                "version": "7.0",
                "lat": 1.0,
                "lon": 2.0,
                "current_temp_f": 70,
                "current_humidity": 50,
                "pressure": 1000.0,
                "pm1_0_atm": 1.0,
                "pm2_5_atm": 2.0,
                "pm10_0_atm": 3.0,
            }
        }

        result = logger._poll_and_convert_local()
        expected_index = int("aabbccddeeff", 16)
        self.assertIn(expected_index, result)
        self.assertEqual(result[expected_index]["device_type"]["id"], 0x002D)

    def test_invalid_payload_is_skipped(self):
        """A local sensor payload missing required keys is skipped, not raised."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_local_sensor_data.return_value = {
            "192.168.1.51": {"unexpected": "payload"}
        }

        result = logger._poll_and_convert_local()
        self.assertEqual(result, {})

    def test_loop_preserves_last_known_good_reading(self):
        """A failed poll does not remove the previous device reading."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._poll_interval = 60
        logger._sensor_indexes = []
        logger._sensor_names = {}
        logger._read_keys = {}
        logger._matter_devices = {1: {"reading": "last-known-good"}}
        logger._lock = threading.Lock()
        logger._poll_and_convert_multiple = Mock(return_value={})

        with patch(
            "purpleair_data_logger.PurpleAirMatterDataLogger.sleep",
            side_effect=StopIteration,
        ):
            with self.assertRaises(StopIteration):
                logger._run_loop_matter({"sensor_indexes": [1]})

        self.assertEqual(logger._matter_devices[1]["reading"], "last-known-good")


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
