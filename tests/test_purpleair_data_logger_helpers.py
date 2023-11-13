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
    DATA_IN_1,
    DATA_OUT_1,
    EXPECTED_VALUE_1,
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

        expected_value = EXPECTED_VALUE_1
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
        data_in = DATA_IN_1
        data_out = DATA_OUT_1

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
        expected_value = EXPECTED_FILE_CONTENTS_6
        self.assertEqual(retval, expected_value)

        file_obj = open(
            "../external_network_hardware_variant_json_samples/3.0+BME280+BME680+PMSX003-A.json",
            "r",
        )
        file_data = load(file_obj)
        file_obj.close()
        retval = flatten_single_sensor_data(file_data)
        expected_value = EXPECTED_FILE_CONTENTS_7
        self.assertEqual(retval, expected_value)

        file_obj = open(
            "../external_network_hardware_variant_json_samples/3.0+OPENLOG+31037 MB+DS3231+BME280+BME68X+PMSX003-A+PMSX003-B.json",
            "r",
        )
        file_data = load(file_obj)
        file_obj.close()
        retval = flatten_single_sensor_data(file_data)
        expected_value = EXPECTED_FILE_CONTENTS_8
        self.assertEqual(retval, expected_value)


    def test_logic_for_storing_single_sensor_data(self):
        """
        """
        pass


    def test_logic_for_storing_multiple_sensors_data(self):
        """
        """
        pass

    def test_logic_for_storing_group_sensors_data(self):
        """
        """
        pass

    def test_logic_for_storing_local_sensors_data(self):
        """
        """
        pass