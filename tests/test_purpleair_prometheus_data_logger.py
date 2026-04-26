#!/usr/bin/env python3

"""
Copyright 2023 carlkidcrypto, All rights reserved.
"""

import unittest
import requests_mock
import sys
from unittest.mock import patch
from prometheus_client import CollectorRegistry

sys.path.append("../")

from tests.helpers import DATA_OUT_1


class PurpleAirPrometheusDataLoggerTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _make_prometheus_logger(self):
        """
        Helper to create a PurpleAirPrometheusDataLogger with a mocked read key,
        a mocked HTTP server, and an isolated CollectorRegistry.
        """
        expected_url_request = "https://api.purpleair.com/v1/keys"
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            with patch(
                "purpleair_data_logger.PurpleAirPrometheusDataLogger.start_http_server"
            ):
                from purpleair_data_logger.PurpleAirPrometheusDataLogger import (
                    PurpleAirPrometheusDataLogger,
                )

                logger = PurpleAirPrometheusDataLogger(
                    PurpleAirApiReadKey="123456789",
                    registry=CollectorRegistry(),
                )
        return logger

    def test_purpleair_prometheus_data_logger_is_correct_type(self):
        """
        Test that PurpleAirPrometheusDataLogger is the right type.
        """
        from purpleair_data_logger.PurpleAirPrometheusDataLogger import (
            PurpleAirPrometheusDataLogger,
        )
        from purpleair_data_logger.PurpleAirDataLogger import PurpleAirDataLogger

        logger = self._make_prometheus_logger()
        self.assertIsInstance(logger, PurpleAirPrometheusDataLogger)
        self.assertIsInstance(logger, PurpleAirDataLogger)

    def test_start_http_server_called_with_port(self):
        """
        Test that start_http_server is called with the configured port.
        """
        expected_url_request = "https://api.purpleair.com/v1/keys"
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            with patch(
                "purpleair_data_logger.PurpleAirPrometheusDataLogger.start_http_server"
            ) as mock_start:
                from purpleair_data_logger.PurpleAirPrometheusDataLogger import (
                    PurpleAirPrometheusDataLogger,
                )

                PurpleAirPrometheusDataLogger(
                    PurpleAirApiReadKey="123456789",
                    prometheus_port=19762,
                    registry=CollectorRegistry(),
                )
                self.assertEqual(mock_start.call_args[0][0], 19762)

    def test_store_sensor_data_updates_gauges(self):
        """
        Test that store_sensor_data sets gauge values for a sensor.
        """
        logger = self._make_prometheus_logger()
        sensor_data = DATA_OUT_1[0]

        logger.store_sensor_data(sensor_data)

        sensor_index = str(sensor_data["sensor_index"])
        self.assertEqual(
            logger._environmental_humidity.labels(sensor_index=sensor_index)._value.get(),
            float(sensor_data["humidity"]),
        )
        self.assertEqual(
            logger._environmental_temperature.labels(sensor_index=sensor_index)._value.get(),
            float(sensor_data["temperature"]),
        )
        self.assertEqual(
            logger._environmental_pressure.labels(sensor_index=sensor_index)._value.get(),
            float(sensor_data["pressure"]),
        )
        self.assertEqual(
            logger._pm2_5.labels(sensor_index=sensor_index)._value.get(),
            float(sensor_data["pm2.5"]),
        )
        self.assertEqual(
            logger._pm10_0.labels(sensor_index=sensor_index)._value.get(),
            float(sensor_data["pm10.0"]),
        )

    def test_store_sensor_data_multiple_sensors(self):
        """
        Test that store_sensor_data correctly handles data from multiple sensors,
        keeping each sensor's gauge value independent.
        """
        logger = self._make_prometheus_logger()

        sensor_data_1 = dict(DATA_OUT_1[0])
        sensor_data_1["pm2.5"] = 5.5

        sensor_data_2 = dict(DATA_OUT_1[1])
        sensor_data_2["pm2.5"] = 12.3

        logger.store_sensor_data(sensor_data_1)
        logger.store_sensor_data(sensor_data_2)

        idx1 = str(sensor_data_1["sensor_index"])
        idx2 = str(sensor_data_2["sensor_index"])

        self.assertEqual(
            logger._pm2_5.labels(sensor_index=idx1)._value.get(),
            5.5,
        )
        self.assertEqual(
            logger._pm2_5.labels(sensor_index=idx2)._value.get(),
            12.3,
        )

    def test_safe_numeric_with_none(self):
        """
        Test that _safe_numeric returns 0.0 for None values.
        """
        logger = self._make_prometheus_logger()
        self.assertEqual(logger._safe_numeric(None), 0.0)

    def test_safe_numeric_with_valid_number(self):
        """
        Test that _safe_numeric converts valid numbers correctly.
        """
        logger = self._make_prometheus_logger()
        self.assertEqual(logger._safe_numeric(42), 42.0)
        self.assertEqual(logger._safe_numeric(3.14), 3.14)
        self.assertEqual(logger._safe_numeric("7.5"), 7.5)

    def test_safe_numeric_with_invalid_string(self):
        """
        Test that _safe_numeric returns 0.0 for non-numeric strings.
        """
        logger = self._make_prometheus_logger()
        self.assertEqual(logger._safe_numeric("not_a_number"), 0.0)

    def test_default_prometheus_port_constant(self):
        """
        Test that the default port constant has the expected value.
        """
        from purpleair_data_logger.PurpleAirPrometheusDataLoggerConstants import (
            PROMETHEUS_DATA_LOGGER_DEFAULT_PORT,
        )

        self.assertEqual(PROMETHEUS_DATA_LOGGER_DEFAULT_PORT, 9760)

    def test_store_sensor_data_station_fields(self):
        """
        Test that store_sensor_data correctly sets station information and status gauge values.
        """
        logger = self._make_prometheus_logger()
        sensor_data = dict(DATA_OUT_1[0])
        sensor_data["rssi"] = -55
        sensor_data["uptime"] = 12345
        sensor_data["memory"] = 20000

        logger.store_sensor_data(sensor_data)

        sensor_index = str(sensor_data["sensor_index"])
        self.assertEqual(
            logger._station_rssi.labels(sensor_index=sensor_index)._value.get(),
            float(sensor_data["rssi"]),
        )
        self.assertEqual(
            logger._station_uptime.labels(sensor_index=sensor_index)._value.get(),
            float(sensor_data["uptime"]),
        )
        self.assertEqual(
            logger._station_memory.labels(sensor_index=sensor_index)._value.get(),
            float(sensor_data["memory"]),
        )

    def test_store_sensor_data_particle_count_fields(self):
        """
        Test that store_sensor_data correctly sets particle count gauge values.
        """
        logger = self._make_prometheus_logger()
        sensor_data = dict(DATA_OUT_1[0])
        sensor_data["0.3_um_count"] = 100.0
        sensor_data["2.5_um_count"] = 50.0
        sensor_data["10.0_um_count"] = 5.0

        logger.store_sensor_data(sensor_data)

        sensor_index = str(sensor_data["sensor_index"])
        self.assertEqual(
            logger._um_count_0_3.labels(sensor_index=sensor_index)._value.get(),
            100.0,
        )
        self.assertEqual(
            logger._um_count_2_5.labels(sensor_index=sensor_index)._value.get(),
            50.0,
        )
        self.assertEqual(
            logger._um_count_10_0.labels(sensor_index=sensor_index)._value.get(),
            5.0,
        )

    def test_store_sensor_data_pm2_5_pseudo_average_fields(self):
        """
        Test that store_sensor_data correctly sets PM2.5 pseudo average gauge values.
        """
        logger = self._make_prometheus_logger()
        sensor_data = dict(DATA_OUT_1[0])
        sensor_data["pm2.5_10minute"] = 8.1
        sensor_data["pm2.5_24hour"] = 11.4
        sensor_data["pm2.5_1week"] = 9.9

        logger.store_sensor_data(sensor_data)

        sensor_index = str(sensor_data["sensor_index"])
        self.assertEqual(
            logger._pm2_5_10minute.labels(sensor_index=sensor_index)._value.get(),
            8.1,
        )
        self.assertEqual(
            logger._pm2_5_24hour.labels(sensor_index=sensor_index)._value.get(),
            11.4,
        )
        self.assertEqual(
            logger._pm2_5_1week.labels(sensor_index=sensor_index)._value.get(),
            9.9,
        )


if __name__ == "__main__":
    unittest.main()
