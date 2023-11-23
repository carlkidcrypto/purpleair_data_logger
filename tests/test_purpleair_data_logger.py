#!/usr/bin/env python3

"""
    Copyright 2023 carlkidcrypto, All rights reserved.
"""


import unittest
import requests_mock
import sys

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
