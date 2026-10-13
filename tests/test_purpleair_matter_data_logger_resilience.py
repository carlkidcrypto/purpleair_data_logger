#!/usr/bin/env python3
"""
Copyright 2025 carlkidcrypto, All rights reserved.

Unit tests for PurpleAirMatterDataLogger resilience, channel averaging,
local sensor polling, and Matter compliance.
"""

import sys
import threading
import time
import unittest
from unittest.mock import Mock, patch

import requests_mock

sys.path.append("../")

from purpleair_api.PurpleAirAPI import PurpleAirAPIError
from purpleair_data_logger.PurpleAirMatterDataLogger import (
    CachedSensor,
    PurpleAirDeviceOfflineError,
    PurpleAirMatterDataLogger,
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
# Tests — Resilience & Failure Isolation
# =============================================================================


class PurpleAirMatterDataLoggerResilienceTest(unittest.TestCase):
    """Tests for failures encountered by the long-running polling loop."""

    def test_unexpected_sensor_error_is_isolated(self):
        """An unexpected client exception falls back to offline device without crashing."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_sensor_data.side_effect = TimeoutError
        logger._max_retries = 1
        logger._retry_backoff_factor = 0.001

        res = logger._poll_and_convert_sensor(282168)
        self.assertIsNotNone(res)
        self.assertEqual(res["_status"], "offline")
        self.assertIsNone(res["_last_seen"])
        self.assertEqual(res["device_type"]["id"], 0x002D)
        self.assertEqual(
            res["clusters"]["air_quality_measurement"]["attributes"]["airQuality"], 0
        )

    def test_purpleair_api_error_is_isolated(self):
        """A PurpleAirAPIError falls back to offline device without crashing."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_sensor_data.side_effect = PurpleAirAPIError(
            "boom"
        )
        logger._max_retries = 1
        logger._retry_backoff_factor = 0.001

        res = logger._poll_and_convert_sensor(282168)
        self.assertIsNotNone(res)
        self.assertEqual(res["_status"], "offline")
        self.assertIsNone(res["_last_seen"])
        self.assertEqual(res["device_type"]["id"], 0x002D)
        self.assertEqual(
            res["clusters"]["air_quality_measurement"]["attributes"]["airQuality"], 0
        )

    def test_sensor_stale_cache_within_grace_period(self):
        """Sensor within offline grace period returns stale cached reading."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_sensor_data.side_effect = PurpleAirAPIError(
            "fail"
        )
        logger._max_retries = 1
        logger._retry_backoff_factor = 0.001
        logger._offline_grace_seconds = 600

        now = time.time()
        initial_device = {
            "device_type": {"id": 0x002D},
            "clusters": {
                "air_quality_measurement": {
                    "attributes": {"airQuality": 1, "aqiRating": 1}
                }
            },
        }
        logger._sensor_cache = {
            282168: CachedSensor(
                data=initial_device, last_seen=now - 200, is_stale=False
            )
        }

        res = logger._poll_and_convert_sensor(282168)
        self.assertIsNotNone(res)
        self.assertEqual(res["_status"], "stale")
        self.assertEqual(res["_last_seen"], now - 200)
        self.assertEqual(
            res["clusters"]["air_quality_measurement"]["attributes"]["airQuality"], 1
        )
        self.assertTrue(logger._sensor_cache[282168].is_stale)

    def test_sensor_offline_after_grace_period(self):
        """Sensor exceeding offline grace period is marked offline with airQuality 0."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_sensor_data.side_effect = PurpleAirAPIError(
            "fail"
        )
        logger._max_retries = 1
        logger._retry_backoff_factor = 0.001
        logger._offline_grace_seconds = 600

        now = time.time()
        initial_device = {
            "device_type": {"id": 0x002D},
            "clusters": {
                "air_quality_measurement": {
                    "attributes": {"airQuality": 2, "aqiRating": 2}
                }
            },
        }
        logger._sensor_cache = {
            282168: CachedSensor(
                data=initial_device, last_seen=now - 700, is_stale=False
            )
        }

        res = logger._poll_and_convert_sensor(282168)
        self.assertIsNotNone(res)
        self.assertEqual(res["_status"], "offline")
        self.assertEqual(res["_last_seen"], now - 700)
        self.assertEqual(
            res["clusters"]["air_quality_measurement"]["attributes"]["airQuality"], 0
        )
        self.assertEqual(
            res["clusters"]["air_quality_measurement"]["attributes"]["aqiRating"], 0
        )

    def test_sensor_recovery_restores_online(self):
        """Sensor recovering from failure updates cache and marks status online."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_sensor_data.return_value = PA_SENSOR_PAYLOAD
        logger._max_retries = 1
        logger._retry_backoff_factor = 0.001
        logger._offline_grace_seconds = 600

        now = time.time()
        stale_device = {
            "device_type": {"id": 0x002D},
            "_status": "stale",
            "_last_seen": now - 300,
        }
        logger._sensor_cache = {
            282168: CachedSensor(data=stale_device, last_seen=now - 300, is_stale=True)
        }

        res = logger._poll_and_convert_sensor(282168)
        self.assertIsNotNone(res)
        self.assertEqual(res["_status"], "online")
        self.assertAlmostEqual(res["_last_seen"], time.time(), delta=5)
        self.assertFalse(logger._sensor_cache[282168].is_stale)

    def test_retry_attempts_then_fails(self):
        """Sensor polling retries configured number of times with backoff before giving up."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_sensor_data.side_effect = PurpleAirAPIError(
            "retry error"
        )
        logger._max_retries = 3
        logger._retry_backoff_factor = 0.001

        res = logger._poll_and_convert_sensor(282168)
        # 1 initial attempt + 3 retries = 4 calls
        self.assertEqual(logger._purpleair_api_obj.request_sensor_data.call_count, 4)
        self.assertEqual(res["_status"], "offline")

    def test_poll_and_convert_multiple_handles_unexpected_exception(self):
        """Unexpected exception in _poll_and_convert_sensor is logged and loop continues."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._poll_and_convert_sensor = Mock(
            side_effect=RuntimeError("unexpected crash")
        )

        results = logger._poll_and_convert_multiple([282168])
        self.assertEqual(results, {})


# =============================================================================
# Tests — Channel Averaging
# =============================================================================


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


# =============================================================================
# Tests — Local Sensor Polling
# =============================================================================


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

    def test_unexpected_local_api_error_returns_empty_dict(self):
        """An unexpected error while polling local sensors yields {}."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_local_sensor_data.side_effect = RuntimeError(
            "unexpected local fail"
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

    def test_partial_sensor_failure_still_converts_available_sensors(self):
        """When 1 of 2 configured local sensors responds, it is converted successfully."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_local_sensor_data.return_value = {
            "192.168.1.50": {
                "SensorId": "aa:bb:cc:dd:ee:ff",
                "hardwarediscovered": "PMS5003",
                "version": "7.0",
                "current_temp_f": 70,
                "current_humidity": 50,
                "pm2_5_atm": 5.0,
            }
        }

        result = logger._poll_and_convert_local()
        expected_index = int("aabbccddeeff", 16)
        self.assertEqual(len(result), 1)
        self.assertIn(expected_index, result)
        self.assertEqual(result[expected_index]["_status"], "online")

    def test_fallback_per_sensor_polling_on_bulk_error(self):
        """When 1 of 2 configured local sensors raises PurpleAirDeviceOfflineError, the other is converted."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        mock_single_50 = Mock()
        mock_single_50.request_local_sensor_data.return_value = {
            "192.168.1.50": {
                "SensorId": "aa:bb:cc:dd:ee:ff",
                "hardwarediscovered": "PMS5003",
                "version": "7.0",
                "pm2_5_atm": 5.0,
            }
        }
        mock_single_51 = Mock()
        mock_single_51.request_local_sensor_data.side_effect = (
            PurpleAirDeviceOfflineError("Device at 192.168.1.51 is offline")
        )
        logger._purpleair_api_obj = [mock_single_50, mock_single_51]

        result = logger._poll_and_convert_local()

        expected_index = int("aabbccddeeff", 16)
        self.assertEqual(len(result), 1)
        self.assertIn(expected_index, result)
        self.assertEqual(result[expected_index]["_status"], "online")

    def test_local_sensor_polling_api_error_and_generic_error(self):
        """When local sensors raise PurpleAirAPIError or generic Exception, errors are handled."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        mock_single_50 = Mock()
        mock_single_50.request_local_sensor_data.side_effect = PurpleAirAPIError(
            "local API error"
        )
        mock_single_51 = Mock()
        mock_single_51.request_local_sensor_data.side_effect = RuntimeError(
            "unexpected crash"
        )
        logger._purpleair_api_obj = [mock_single_50, mock_single_51]

        result = logger._poll_and_convert_local()
        self.assertEqual(result, {})

    def test_invalid_payload_is_skipped(self):
        """A local sensor payload missing required keys is skipped, not raised."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_local_sensor_data.return_value = {
            "192.168.1.51": {"unexpected": "payload"}
        }

        result = logger._poll_and_convert_local()
        self.assertEqual(result, {})

    def test_local_sensor_falls_back_to_cache_when_unreachable(self):
        """Unreachable local sensor falls back to cached reading with stale/offline status."""
        logger = PurpleAirMatterDataLogger.__new__(PurpleAirMatterDataLogger)
        logger._purpleair_api_obj = Mock()
        logger._purpleair_api_obj.request_local_sensor_data.return_value = {}
        logger._offline_grace_seconds = 600

        now = time.time()
        sensor_index = 12345
        cached_device = {
            "device_type": {"id": 0x002D},
            "clusters": {
                "air_quality_measurement": {
                    "attributes": {"airQuality": 1, "aqiRating": 1}
                }
            },
        }
        logger._sensor_cache = {
            sensor_index: CachedSensor(
                data=cached_device, last_seen=now - 100, is_stale=False
            )
        }

        # Within grace period: status is stale
        result = logger._poll_and_convert_local()
        self.assertIn(sensor_index, result)
        self.assertEqual(result[sensor_index]["_status"], "stale")
        self.assertEqual(
            result[sensor_index]["clusters"]["air_quality_measurement"]["attributes"][
                "airQuality"
            ],
            1,
        )

        # Beyond grace period: status is offline and airQuality is 0
        logger._sensor_cache[sensor_index].last_seen = now - 700
        result_offline = logger._poll_and_convert_local()
        self.assertIn(sensor_index, result_offline)
        self.assertEqual(result_offline[sensor_index]["_status"], "offline")
        self.assertEqual(
            result_offline[sensor_index]["clusters"]["air_quality_measurement"][
                "attributes"
            ]["airQuality"],
            0,
        )

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
# Tests — Matter Device Type Correctness
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
        self.assertIsInstance(summary["epa_aqi"], (int, float))
        self.assertGreaterEqual(summary["epa_aqi"], 0)


if __name__ == "__main__":
    unittest.main()
