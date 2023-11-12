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
