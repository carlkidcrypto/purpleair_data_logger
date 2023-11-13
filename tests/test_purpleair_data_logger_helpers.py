#!/usr/bin/env python3

"""
    Copyright 2023 carlkidcrypto, All rights reserved.
"""


import unittest
import requests_mock
import sys
from json import load

sys.path.append("../")

from purpleair_data_logger.PurpleAirDataLoggerHelpers import (
    generate_common_arg_parser,
    validate_sensor_data_before_insert,
    construct_store_sensor_data_type,
    flatten_single_sensor_data,
)

from helpers import (
    EXPECTED_FILE_CONTENTS_1,
    EXPECTED_FILE_CONTENTS_2,
    EXPECTED_FILE_CONTENTS_3,
    EXPECTED_FILE_CONTENTS_4,
    EXPECTED_FILE_CONTENTS_5,
    EXPECTED_FILE_CONTENTS_6,
    EXPECTED_FILE_CONTENTS_7,
    EXPECTED_FILE_CONTENTS_8,
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

        # The sensors data will look something like this:
        # {'api_version': 'V1.0.11-0.0.34', 'time_stamp': 1659710288, 'data_time_stamp': 1659710232,
        # 'max_age': 604800, 'firmware_default_version': '7.00', 'fields': ['sensor_index', 'name'],
        # 'data': [[131075, 'Mariners Bluff'], [131079, 'BRSKBV-outside'], [131077, 'BEE Patio'],
        # ... ]}

        data_in = {
            "api_version": "V1.0.11-0.0.34",
            "time_stamp": 1659710288,
            "data_time_stamp": 1659710232,
            "max_age": 604800,
            "firmware_default_version": "7.00",
            "fields": ["sensor_index", "name"],
            "data": [[1, "TEST1"], [2, "TEST2"], [3, "TEST3"]],
        }

        data_out = [
            {
                "data_time_stamp": 1659710232,
                "sensor_index": 1,
                "name": "TEST1",
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
            },
            {
                "data_time_stamp": 1659710232,
                "sensor_index": 2,
                "name": "TEST2",
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
            },
            {
                "data_time_stamp": 1659710232,
                "sensor_index": 3,
                "name": "TEST3",
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
            },
        ]
        retval = construct_store_sensor_data_type(data_in)
        self.assertEqual(retval, data_out)

    def test_flatten_single_sensor_data(self):
        """
        Test that the flatten_single_sensor_data can handle all the sample responses under ../external_network_hardware_variant_json_samples/*.json
        """

        file_obj = open(
            "../external_network_hardware_variant_json_samples/1.0+1M+PMSX003-O.json",
            "r",
        )
        file_data = load(file_obj)
        file_obj.close()
        retval = flatten_single_sensor_data(file_data)
        expected_value = EXPECTED_FILE_CONTENTS_1
        self.assertEqual(retval, expected_value)

        file_obj = open(
            "../external_network_hardware_variant_json_samples/2.0+1M+PMSX003-A.json",
            "r",
        )
        file_data = load(file_obj)
        file_obj.close()
        retval = flatten_single_sensor_data(file_data)
        expected_value = EXPECTED_FILE_CONTENTS_2
        self.assertEqual(retval, expected_value)

        file_obj = open(
            "../external_network_hardware_variant_json_samples/2.0+BME280+PMSX003-A.json",
            "r",
        )
        file_data = load(file_obj)
        file_obj.close()
        retval = flatten_single_sensor_data(file_data)
        expected_value = EXPECTED_FILE_CONTENTS_3
        self.assertEqual(retval, expected_value)

        file_obj = open(
            "../external_network_hardware_variant_json_samples/2.0+BME280+PMSX003-B+PMSX003-A.json",
            "r",
        )
        file_data = load(file_obj)
        file_obj.close()
        retval = flatten_single_sensor_data(file_data)
        expected_value = EXPECTED_FILE_CONTENTS_4
        self.assertEqual(retval, expected_value)

        file_obj = open(
            "../external_network_hardware_variant_json_samples/2.0+OPENLOG+31037 MB+DS3231+BME280+PMSX003-A.json",
            "r",
        )
        file_data = load(file_obj)
        file_obj.close()
        retval = flatten_single_sensor_data(file_data)
        expected_value = EXPECTED_FILE_CONTENTS_5
        self.assertEqual(retval, expected_value)

        file_obj = open(
            "../external_network_hardware_variant_json_samples/2.0+OPENLOG+31037 MB+DS3231+BME280+PMSX003-B+PMSX003-A.json",
            "r",
        )
        file_data = load(file_obj)
        file_obj.close()
        retval = flatten_single_sensor_data(file_data)
        print(retval)
        expected_value = EXPECTED_FILE_CONTENTS_6
        self.assertEqual(retval, expected_value)
