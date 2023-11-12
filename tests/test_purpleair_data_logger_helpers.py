#!/usr/bin/env python3

"""
    Copyright 2023 carlkidcrypto, All rights reserved.
"""


import unittest
import requests_mock
import sys

sys.path.append("../")

from purpleair_data_logger.PurpleAirDataLoggerHelpers import (
    generate_common_arg_parser,
    validate_sensor_data_before_insert,
    construct_store_sensor_data_type,
)


class PurpleAirDataLoggerHelpersTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_generate_common_arg_parser_with_valid_args(self):
        """
        Test that our generator makes the common arguments that all PADLS use.
        """

        retval = generate_common_arg_parser("TEST")
        self.assertEqual(retval.description, "TEST")
        self.assertTrue(retval.parse_args(["-paa_read_key", "2"]))
        self.assertTrue(retval.parse_args(["-paa_write_key", "2"]))
        self.assertTrue(
            retval.parse_args(["-paa_single_sensor_request_json_file", "2"])
        )
        self.assertTrue(
            retval.parse_args(["-paa_multiple_sensor_request_json_file", "2"])
        )
        self.assertTrue(retval.parse_args(["-paa_group_sensor_request_json_file", "2"]))
        self.assertTrue(retval.parse_args(["-paa_local_sensor_request_json_file", "2"]))

    def test_validate_sensor_data_before_insert(self):
        """
        Test that our validator makes any missing fields their defaults
        """

        expected_value = {
            "name": "",
            "icon": 0,
            "model": "",
            "hardware": "",
            "location_type": 0,
            "private": 0,
            "latitude": 0.0,
            "longitude": 0.0,
            "altitude": 0.0,
            "position_rating": 0,
            "led_brightness": 0,
            "firmware_version": "",
            "firmware_upgrade": "",
            "rssi": 0,
            "uptime": 0,
            "pa_latency": 0,
            "memory": 0,
            "last_seen": 0,
            "last_modified": 0,
            "date_created": 0,
            "channel_state": 0,
            "channel_flags": 0,
            "channel_flags_manual": 0,
            "channel_flags_auto": 0,
            "confidence": 0,
            "confidence_manual": 0,
            "confidence_auto": 0,
            "humidity": 0,
            "humidity_a": 0,
            "humidity_b": 0,
            "temperature": 0,
            "temperature_a": 0,
            "temperature_b": 0,
            "pressure": 0.0,
            "pressure_a": 0.0,
            "pressure_b": 0.0,
            "voc": 0.0,
            "voc_a": 0.0,
            "voc_b": 0.0,
            "ozone1": 0.0,
            "analog_input": 0.0,
            "pm1.0": 0.0,
            "pm1.0_a": 0.0,
            "pm1.0_b": 0.0,
            "pm1.0_atm": 0.0,
            "pm1.0_atm_a": 0.0,
            "pm1.0_atm_b": 0.0,
            "pm1.0_cf_1": 0.0,
            "pm1.0_cf_1_a": 0.0,
            "pm1.0_cf_1_b": 0.0,
            "pm2.5_alt": 0.0,
            "pm2.5_alt_a": 0.0,
            "pm2.5_alt_b": 0.0,
            "pm2.5": 0.0,
            "pm2.5_a": 0.0,
            "pm2.5_b": 0.0,
            "pm2.5_atm": 0.0,
            "pm2.5_atm_a": 0.0,
            "pm2.5_atm_b": 0.0,
            "pm2.5_cf_1": 0.0,
            "pm2.5_cf_1_a": 0.0,
            "pm2.5_cf_1_b": 0.0,
            "pm2.5_10minute": 0.0,
            "pm2.5_10minute_a": 0.0,
            "pm2.5_10minute_b": 0.0,
            "pm2.5_30minute": 0.0,
            "pm2.5_30minute_a": 0.0,
            "pm2.5_30minute_b": 0.0,
            "pm2.5_60minute": 0.0,
            "pm2.5_60minute_a": 0.0,
            "pm2.5_60minute_b": 0.0,
            "pm2.5_6hour": 0.0,
            "pm2.5_6hour_a": 0.0,
            "pm2.5_6hour_b": 0.0,
            "pm2.5_24hour": 0.0,
            "pm2.5_24hour_a": 0.0,
            "pm2.5_24hour_b": 0.0,
            "pm2.5_1week": 0.0,
            "pm2.5_1week_a": 0.0,
            "pm2.5_1week_b": 0.0,
            "pm10.0": 0.0,
            "pm10.0_a": 0.0,
            "pm10.0_b": 0.0,
            "pm10.0_atm": 0.0,
            "pm10.0_atm_a": 0.0,
            "pm10.0_atm_b": 0.0,
            "pm10.0_cf_1": 0.0,
            "pm10.0_cf_1_a": 0.0,
            "pm10.0_cf_1_b": 0.0,
            "0.3_um_count": 0.0,
            "0.3_um_count_a": 0.0,
            "0.3_um_count_b": 0.0,
            "0.5_um_count": 0.0,
            "0.5_um_count_a": 0.0,
            "0.5_um_count_b": 0.0,
            "1.0_um_count": 0.0,
            "1.0_um_count_a": 0.0,
            "1.0_um_count_b": 0.0,
            "2.5_um_count": 0.0,
            "2.5_um_count_a": 0.0,
            "2.5_um_count_b": 0.0,
            "5.0_um_count": 0.0,
            "5.0_um_count_a": 0.0,
            "5.0_um_count_b": 0.0,
            "10.0_um_count": 0.0,
            "10.0_um_count_a": 0.0,
            "10.0_um_count_b": 0.0,
            "primary_id_a": 0,
            "primary_key_a": "",
            "secondary_id_a": 0,
            "secondary_key_a": "",
            "primary_id_b": 0,
            "primary_key_b": "",
            "secondary_id_b": 0,
            "secondary_key_b": "",
        }
        self.assertEqual(validate_sensor_data_before_insert({}), expected_value)

    
    def test_construct_store_sensor_data_type(self):
        """
        Test that our contructor makes the dict data type that the PurpleAirDataLogger.store_sensor_data method expects.
        """

        #construct_store_sensor_data_type()
