#!/usr/bin/env python3

"""
Copyright 2023 carlkidcrypto, All rights reserved.
"""

import unittest
import requests_mock
import sys
import json
import os
import tempfile
from unittest.mock import MagicMock, patch

sys.path.append("../")

from purpleair_data_logger.PurpleAirDataLogger import (
    PurpleAirDataLoggerError,
    PurpleAirDataLogger,
)


class PurpleAirDataLoggerTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_purpleair_data_logger_error(self):
        """
        Test that PurpleAirDataLoggerError is the right type.
        """

        # Setup
        self.error_msg_str = "This is a test!"

        # Action
        retval = PurpleAirDataLoggerError(self.error_msg_str)

        # Expected Result
        self.assertEqual(retval.message, self.error_msg_str)
        self.assertEqual(retval.__class__, PurpleAirDataLoggerError)

    def test_purpleair_data_logger_getters_setters(self):
        """
        Test PurpleAirDataLogger getters/setters
        """

        # Setup
        expected_url_request = "https://api.purpleair.com/v1/keys"

        # Action and Expected Result
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            padl = PurpleAirDataLogger(PurpleAirApiReadKey="123456789")

        padl.send_request_every_x_seconds = 100
        self.assertEqual(padl.send_request_every_x_seconds, 100)

    def test_purpleair_data_logger_store_sensor_data(self):
        """
        Test PurpleAirDataLogger store_sensor_data method raises, since inherting classes
        must implment it.
        """

        # Setup
        expected_url_request = "https://api.purpleair.com/v1/keys"

        # Action and Expected Result
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            padl = PurpleAirDataLogger(PurpleAirApiReadKey="123456789")

        with self.assertRaises(NotImplementedError):
            padl.store_sensor_data({})

    def test_purpleair_data_logger_setter_raises_on_low_value(self):
        """
        Test that PurpleAirDataLoggerError is raised when setting
        send_request_every_x_seconds to a value less than 60.
        """

        expected_url_request = "https://api.purpleair.com/v1/keys"

        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            padl = PurpleAirDataLogger(PurpleAirApiReadKey="123456789")

        with self.assertRaises(PurpleAirDataLoggerError):
            padl.send_request_every_x_seconds = 59

    def _make_padl_with_mock(self):
        """Helper to create a PurpleAirDataLogger with a mocked read key."""
        expected_url_request = "https://api.purpleair.com/v1/keys"
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            padl = PurpleAirDataLogger(PurpleAirApiReadKey="123456789")
        return padl

    def test_validate_parameters_and_run_all_none_raises(self):
        """
        Test that validate_parameters_and_run raises when all args are None.
        """
        padl = self._make_padl_with_mock()
        with self.assertRaises(PurpleAirDataLoggerError):
            padl.validate_parameters_and_run()

    def test_validate_parameters_and_run_multiple_provided_raises(self):
        """
        Test that validate_parameters_and_run raises when multiple args are provided.
        """
        padl = self._make_padl_with_mock()
        with self.assertRaises(PurpleAirDataLoggerError):
            padl.validate_parameters_and_run(
                paa_single_sensor_request_json_file="a.json",
                paa_multiple_sensor_request_json_file="b.json",
            )

    def test_validate_parameters_and_run_single_sensor(self):
        """
        Test that validate_parameters_and_run calls the single-sensor run loop.
        """
        padl = self._make_padl_with_mock()
        config = {"poll_interval_seconds": 60, "sensor_index": 53, "read_key": None, "fields": None}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config, f)
            tmp_path = f.name
        try:
            with patch.object(
                padl, "_run_loop_for_storing_single_sensor_data"
            ) as mock_run:
                padl.validate_parameters_and_run(
                    paa_single_sensor_request_json_file=tmp_path
                )
                mock_run.assert_called_once_with(config)
        finally:
            os.unlink(tmp_path)

    def test_validate_parameters_and_run_multiple_sensors(self):
        """
        Test that validate_parameters_and_run calls the multiple-sensor run loop.
        """
        padl = self._make_padl_with_mock()
        config = {"poll_interval_seconds": 60, "fields": "name"}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config, f)
            tmp_path = f.name
        try:
            with patch.object(
                padl, "_run_loop_for_storing_multiple_sensors_data"
            ) as mock_run:
                padl.validate_parameters_and_run(
                    paa_multiple_sensor_request_json_file=tmp_path
                )
                mock_run.assert_called_once_with(config)
        finally:
            os.unlink(tmp_path)

    def test_validate_parameters_and_run_group_sensors(self):
        """
        Test that validate_parameters_and_run calls the group-sensor run loop.
        """
        padl = self._make_padl_with_mock()
        config = {"poll_interval_seconds": 60, "sensor_group_name": "test", "add_sensors_to_group": False, "sensor_index_list": [], "fields": "name"}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config, f)
            tmp_path = f.name
        try:
            with patch.object(
                padl, "_run_loop_for_storing_group_sensors_data"
            ) as mock_run:
                padl.validate_parameters_and_run(
                    paa_group_sensor_request_json_file=tmp_path
                )
                mock_run.assert_called_once_with(config)
        finally:
            os.unlink(tmp_path)

    def test_validate_parameters_and_run_local_sensors(self):
        """
        Test that validate_parameters_and_run calls the local-sensor run loop.
        """
        padl = self._make_padl_with_mock()
        config = {"sensor_ip_list": ["192.168.1.1"], "poll_interval_seconds": 60}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config, f)
            tmp_path = f.name
        try:
            with patch.object(
                padl, "_run_loop_for_storing_local_sensors_data"
            ) as mock_run:
                padl.validate_parameters_and_run(
                    paa_local_sensor_request_json_file=tmp_path
                )
                mock_run.assert_called_once_with(config)
        finally:
            os.unlink(tmp_path)

    def test_run_loop_for_storing_single_sensor_data(self):
        """
        Test that _run_loop_for_storing_single_sensor_data sets the poll interval
        and calls logic once before sleep breaks out.
        """
        padl = self._make_padl_with_mock()
        config = {"poll_interval_seconds": 65, "sensor_index": 53, "read_key": None, "fields": None}

        with patch(
            "purpleair_data_logger.PurpleAirDataLogger.logic_for_storing_single_sensor_data"
        ) as mock_logic, patch(
            "purpleair_data_logger.PurpleAirDataLogger.sleep",
            side_effect=StopIteration,
        ):
            with self.assertRaises(StopIteration):
                padl._run_loop_for_storing_single_sensor_data(config)
        mock_logic.assert_called_once_with(padl, config)
        self.assertEqual(padl.send_request_every_x_seconds, 65)

    def test_run_loop_for_storing_multiple_sensors_data(self):
        """
        Test that _run_loop_for_storing_multiple_sensors_data sets the poll interval
        and calls logic once before sleep breaks out.
        """
        padl = self._make_padl_with_mock()
        config = {"poll_interval_seconds": 65, "fields": "name"}

        with patch(
            "purpleair_data_logger.PurpleAirDataLogger.logic_for_storing_multiple_sensors_data"
        ) as mock_logic, patch(
            "purpleair_data_logger.PurpleAirDataLogger.sleep",
            side_effect=StopIteration,
        ):
            with self.assertRaises(StopIteration):
                padl._run_loop_for_storing_multiple_sensors_data(config)
        mock_logic.assert_called_once_with(padl, config)
        self.assertEqual(padl.send_request_every_x_seconds, 65)

    def test_run_loop_for_storing_group_sensors_data(self):
        """
        Test that _run_loop_for_storing_group_sensors_data sets the poll interval
        and calls logic once before sleep breaks out.
        """
        padl = self._make_padl_with_mock()
        config = {"poll_interval_seconds": 65, "fields": "name", "sensor_group_name": "test"}

        with patch(
            "purpleair_data_logger.PurpleAirDataLogger.logic_for_storing_group_sensors_data",
            return_value=42,
        ) as mock_logic, patch(
            "purpleair_data_logger.PurpleAirDataLogger.sleep",
            side_effect=StopIteration,
        ):
            with self.assertRaises(StopIteration):
                padl._run_loop_for_storing_group_sensors_data(config)
        mock_logic.assert_called_once_with(padl, None, config)
        self.assertEqual(padl.send_request_every_x_seconds, 65)

    def test_run_loop_for_storing_local_sensors_data(self):
        """
        Test that _run_loop_for_storing_local_sensors_data calls logic once
        before sleep breaks out.
        """
        padl = self._make_padl_with_mock()
        config = {"sensor_ip_list": ["192.168.1.1"], "poll_interval_seconds": 65}

        with patch(
            "purpleair_data_logger.PurpleAirDataLogger.logic_for_storing_local_sensors_data"
        ) as mock_logic, patch(
            "purpleair_data_logger.PurpleAirDataLogger.sleep",
            side_effect=StopIteration,
        ):
            with self.assertRaises(StopIteration):
                padl._run_loop_for_storing_local_sensors_data(config)
        mock_logic.assert_called_once_with(padl, config)
