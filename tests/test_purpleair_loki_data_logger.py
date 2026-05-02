#!/usr/bin/env python3

"""
Copyright 2023 carlkidcrypto, All rights reserved.
"""

import unittest
import requests_mock as requests_mock_module
import sys
import json
from unittest.mock import MagicMock, patch

sys.path.append("../")

from purpleair_data_logger.PurpleAirLokiDataLogger import PurpleAirLokiDataLogger

from helpers import DATA_OUT_1

LOKI_PUSH_URL = "http://localhost:3100/loki/api/v1/push"
PURPLEAIR_KEYS_URL = "https://api.purpleair.com/v1/keys"

# A full sensor data dict (borrowed from helpers.DATA_OUT_1[0])
SAMPLE_SENSOR_DATA = DATA_OUT_1[0]


class PurpleAirLokiDataLoggerTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _make_loki_logger(
        self, loki_url="http://localhost:3100", loki_usr=None, loki_pwd=None
    ):
        """Helper to create a PurpleAirLokiDataLogger with mocked PurpleAir API key validation."""
        with requests_mock_module.Mocker() as m:
            m.get(
                PURPLEAIR_KEYS_URL,
                text='{"api_version": "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            logger = PurpleAirLokiDataLogger(
                PurpleAirApiReadKey="test-read-key",
                loki_url=loki_url,
                loki_usr=loki_usr,
                loki_pwd=loki_pwd,
            )
        return logger

    def test_init_sets_loki_push_url(self):
        """
        Test that __init__ correctly constructs the Loki push endpoint URL.
        """
        logger = self._make_loki_logger(loki_url="http://localhost:3100")
        self.assertEqual(logger._loki_url, LOKI_PUSH_URL)

    def test_init_strips_trailing_slash_from_loki_url(self):
        """
        Test that __init__ strips a trailing slash from the provided loki_url.
        """
        logger = self._make_loki_logger(loki_url="http://localhost:3100/")
        self.assertEqual(logger._loki_url, LOKI_PUSH_URL)

    def test_init_stores_loki_credentials(self):
        """
        Test that __init__ stores loki_usr and loki_pwd.
        """
        logger = self._make_loki_logger(loki_usr="admin", loki_pwd="secret")
        self.assertEqual(logger._loki_usr, "admin")
        self.assertEqual(logger._loki_pwd, "secret")

    def test_init_credentials_default_to_none(self):
        """
        Test that loki_usr and loki_pwd default to None when not provided.
        """
        logger = self._make_loki_logger()
        self.assertIsNone(logger._loki_usr)
        self.assertIsNone(logger._loki_pwd)

    def test_store_sensor_data_posts_to_loki(self):
        """
        Test that store_sensor_data performs a POST to the Loki push endpoint.
        """
        logger = self._make_loki_logger()

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=204)
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))
            self.assertEqual(m.call_count, 1)
            self.assertEqual(m.last_request.method, "POST")
            self.assertEqual(m.last_request.url, LOKI_PUSH_URL)

    def test_store_sensor_data_sends_json_content_type(self):
        """
        Test that store_sensor_data sends requests with Content-Type application/json.
        """
        logger = self._make_loki_logger()

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=204)
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))
            self.assertIn("application/json", m.last_request.headers["Content-Type"])

    def test_store_sensor_data_payload_has_nine_streams(self):
        """
        Test that store_sensor_data sends a payload with nine log streams
        (one per data group).
        """
        logger = self._make_loki_logger()

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=204)
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))
            payload = json.loads(m.last_request.body)
            self.assertIn("streams", payload)
            self.assertEqual(len(payload["streams"]), 9)

    def test_store_sensor_data_stream_labels_contain_sensor_index(self):
        """
        Test that each stream in the Loki push payload carries the correct sensor_index label.
        """
        logger = self._make_loki_logger()

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=204)
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))
            payload = json.loads(m.last_request.body)
            for stream in payload["streams"]:
                self.assertEqual(
                    stream["stream"]["sensor_index"],
                    str(SAMPLE_SENSOR_DATA["sensor_index"]),
                )

    def test_store_sensor_data_stream_labels_contain_expected_data_groups(self):
        """
        Test that the Loki push payload contains a stream for each expected data group.
        """
        logger = self._make_loki_logger()
        expected_data_groups = {
            "station_information_and_status_fields",
            "environmental_fields",
            "miscellaneous_fields",
            "pm1_0_fields",
            "pm2_5_fields",
            "pm2_5_pseudo_average_fields",
            "pm10_0_fields",
            "particle_count_fields",
            "thingspeak_fields",
        }

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=204)
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))
            payload = json.loads(m.last_request.body)
            actual_data_groups = {s["stream"]["data_group"] for s in payload["streams"]}
            self.assertEqual(actual_data_groups, expected_data_groups)

    def test_store_sensor_data_timestamp_in_nanoseconds(self):
        """
        Test that the timestamp in each Loki log entry is the data_time_stamp converted
        to nanoseconds (multiplied by 1_000_000_000).
        """
        logger = self._make_loki_logger()
        expected_ts_ns = str(SAMPLE_SENSOR_DATA["data_time_stamp"] * 1_000_000_000)

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=204)
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))
            payload = json.loads(m.last_request.body)
            for stream in payload["streams"]:
                self.assertEqual(stream["values"][0][0], expected_ts_ns)

    def test_store_sensor_data_log_line_is_valid_json(self):
        """
        Test that every log entry value in the Loki payload is a valid JSON string.
        """
        logger = self._make_loki_logger()

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=204)
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))
            payload = json.loads(m.last_request.body)
            for stream in payload["streams"]:
                log_line = stream["values"][0][1]
                # This should not raise
                parsed = json.loads(log_line)
                self.assertIsInstance(parsed, dict)

    def test_store_sensor_data_with_basic_auth(self):
        """
        Test that store_sensor_data sends the correct basic auth credentials when provided.
        """
        logger = self._make_loki_logger(loki_usr="admin", loki_pwd="secret")

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=204)
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))
            # requests encodes Basic auth in the Authorization header
            self.assertIn("Authorization", m.last_request.headers)
            self.assertTrue(
                m.last_request.headers["Authorization"].startswith("Basic ")
            )

    def test_store_sensor_data_increments_error_counter_on_http_error(self):
        """
        Test that store_sensor_data increments _data_error_counter when Loki returns
        an HTTP error response.
        """
        logger = self._make_loki_logger()
        self.assertEqual(logger._data_error_counter, 0)

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=500)
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))
            self.assertEqual(logger._data_error_counter, 1)

    def test_store_sensor_data_does_not_raise_on_http_error(self):
        """
        Test that store_sensor_data does not propagate HTTP errors - it handles them
        gracefully and increments the error counter instead.
        """
        logger = self._make_loki_logger()

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=503)
            # Should not raise
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))

    def test_store_sensor_data_environmental_fields_log_line_content(self):
        """
        Test that the environmental_fields stream log line contains the expected keys.
        """
        logger = self._make_loki_logger()
        expected_keys = {
            "data_time_stamp",
            "sensor_index",
            "humidity",
            "humidity_a",
            "humidity_b",
            "temperature",
            "temperature_a",
            "temperature_b",
            "pressure",
            "pressure_a",
            "pressure_b",
        }

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=204)
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))
            payload = json.loads(m.last_request.body)
            env_stream = next(
                s
                for s in payload["streams"]
                if s["stream"]["data_group"] == "environmental_fields"
            )
            log_line = json.loads(env_stream["values"][0][1])
            self.assertEqual(set(log_line.keys()), expected_keys)

    def test_store_sensor_data_station_fields_log_line_content(self):
        """
        Test that the station_information_and_status_fields stream log line contains
        the expected keys.
        """
        logger = self._make_loki_logger()
        expected_keys = {
            "data_time_stamp",
            "sensor_index",
            "name",
            "icon",
            "model",
            "hardware",
            "location_type",
            "private",
            "latitude",
            "longitude",
            "altitude",
            "position_rating",
            "led_brightness",
            "firmware_version",
            "firmware_upgrade",
            "rssi",
            "uptime",
            "pa_latency",
            "memory",
            "last_seen",
            "last_modified",
            "date_created",
            "channel_state",
            "channel_flags",
            "channel_flags_manual",
            "channel_flags_auto",
            "confidence",
            "confidence_manual",
            "confidence_auto",
        }

        with requests_mock_module.Mocker() as m:
            m.post(LOKI_PUSH_URL, status_code=204)
            logger.store_sensor_data(dict(SAMPLE_SENSOR_DATA))
            payload = json.loads(m.last_request.body)
            station_stream = next(
                s
                for s in payload["streams"]
                if s["stream"]["data_group"] == "station_information_and_status_fields"
            )
            log_line = json.loads(station_stream["values"][0][1])
            self.assertEqual(set(log_line.keys()), expected_keys)


if __name__ == "__main__":
    unittest.main()
