#!/usr/bin/env python3

"""
    Copyright 2023 carlkidcrypto, All rights reserved.
"""


import unittest
from unittest.mock import MagicMock, patch
import requests_mock
import sys
from json import load, dumps

sys.path.append("../")

from purpleair_data_logger.PurpleAirDataLoggerHelpers import (
    generate_common_arg_parser,
    validate_sensor_data_before_insert,
    construct_store_sensor_data_type,
    flatten_single_sensor_data,
    logic_for_storing_single_sensor_data,
    logic_for_storing_multiple_sensors_data,
    logic_for_storing_group_sensors_data,
    logic_for_storing_local_sensors_data,
)

from purpleair_data_logger.PurpleAirDataLogger import PurpleAirDataLogger

from helpers import (
    DATA_IN_1,
    DATA_IN_2,
    LOCAL_API_DATA_IN_1,
    LOCAL_API_DATA_IN_2,
    DATA_OUT_1,
    DATA_OUT_2,
    DATA_OUT_3,
    DATA_OUT_4,
    DATA_OUT_5,
    LOCAL_API_DATA_OUT_1,
    LOCAL_API_DATA_OUT_2,
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
        Test the main logic for the PurpleAirDataLogger.`_run_loop_for_storing_single_sensor_data` method.
        """

        # Setup
        expected_url_request = "https://api.purpleair.com/v1/keys"
        padl = None
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            padl = PurpleAirDataLogger(PurpleAirApiReadKey="123456789")
            padl.store_sensor_data = MagicMock(name="store_sensor_data")
        json_config_file = {
            "sensor_index": "1111",
            "read_key": None,
            "fields": ["name", "icon", "model", "hardware", "location_type"],
        }

        # Action & Expected Result
        expected_url_request = "https://api.purpleair.com/v1/sensors/1111?fields=%5B'name','icon','model','hardware','location_type'%5D"
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text=f"{dumps(DATA_IN_2)}",
                status_code=200,
            )
            logic_for_storing_single_sensor_data(padl, json_config_file)
            padl.store_sensor_data.return_value = None
            padl.store_sensor_data.assert_called_once_with(DATA_OUT_2)

    def test_logic_for_storing_multiple_sensors_data(self):
        """
        Test the main logic for the PurpleAirDataLogger.`_run_loop_for_storing_multiple_sensors_data` method.
        """

        # Setup
        expected_url_request = "https://api.purpleair.com/v1/keys"
        padl = None
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            padl = PurpleAirDataLogger(PurpleAirApiReadKey="123456789")
            padl.store_sensor_data = MagicMock(name="store_sensor_data")
        json_config_file = {
            "poll_interval_seconds": 60,
            "fields": "name, icon, model, hardware, location_type, private, latitude, longitude, altitude, position_rating, led_brightness, firmware_version, firmware_upgrade, rssi, uptime, pa_latency, memory, last_seen, last_modified, date_created, channel_state, channel_flags, channel_flags_manual, channel_flags_auto, confidence, confidence_manual, confidence_auto,humidity, humidity_a, humidity_b, temperature, temperature_a, temperature_b, pressure, pressure_a, pressure_b,voc, voc_a, voc_b, ozone1, analog_input,pm1.0, pm1.0_a, pm1.0_b, pm1.0_atm, pm1.0_atm_a, pm1.0_atm_b, pm1.0_cf_1, pm1.0_cf_1_a,pm1.0_cf_1_b,pm2.5_alt, pm2.5_alt_a, pm2.5_alt_b, pm2.5, pm2.5_a, pm2.5_b, pm2.5_atm, pm2.5_atm_a, pm2.5_atm_b, pm2.5_cf_1, pm2.5_cf_1_a, pm2.5_cf_1_b,pm2.5_10minute, pm2.5_10minute_a, pm2.5_10minute_b, pm2.5_30minute, pm2.5_30minute_a, pm2.5_30minute_b, pm2.5_60minute, pm2.5_60minute_a, pm2.5_60minute_b, pm2.5_6hour, pm2.5_6hour_a, pm2.5_6hour_b,pm2.5_24hour, pm2.5_24hour_a, pm2.5_24hour_b, pm2.5_1week, pm2.5_1week_a, pm2.5_1week_b,pm10.0, pm10.0_a, pm10.0_b, pm10.0_atm, pm10.0_atm_a, pm10.0_atm_b, pm10.0_cf_1, pm10.0_cf_1_a, pm10.0_cf_1_b,0.3_um_count,0.3_um_count_a,0.3_um_count_b,0.5_um_count,0.5_um_count_a,0.5_um_count_b,1.0_um_count,1.0_um_count_a,1.0_um_count_b,2.5_um_count,2.5_um_count_a,2.5_um_count_b,5.0_um_count,5.0_um_count_a,5.0_um_count_b,10.0_um_count,10.0_um_count_a,10.0_um_count_b,primary_id_a, primary_key_a, secondary_id_a, secondary_key_a, primary_id_b, primary_key_b, secondary_id_b, secondary_key_b",
            "location_type": None,
            "read_keys": None,
            "show_only": None,
            "modified_since": None,
            "max_age": None,
            "nwlng": None,
            "nwlat": None,
            "selng": None,
            "selat": None,
        }

        # Action & Expected Result
        expected_url_request = "https://api.purpleair.com/v1/sensors/?fields=name,icon,model,hardware,location_type,private,latitude,longitude,altitude,position_rating,led_brightness,firmware_version,firmware_upgrade,rssi,uptime,pa_latency,memory,last_seen,last_modified,date_created,channel_state,channel_flags,channel_flags_manual,channel_flags_auto,confidence,confidence_manual,confidence_auto,humidity,humidity_a,humidity_b,temperature,temperature_a,temperature_b,pressure,pressure_a,pressure_b,voc,voc_a,voc_b,ozone1,analog_input,pm1.0,pm1.0_a,pm1.0_b,pm1.0_atm,pm1.0_atm_a,pm1.0_atm_b,pm1.0_cf_1,pm1.0_cf_1_a,pm1.0_cf_1_b,pm2.5_alt,pm2.5_alt_a,pm2.5_alt_b,pm2.5,pm2.5_a,pm2.5_b,pm2.5_atm,pm2.5_atm_a,pm2.5_atm_b,pm2.5_cf_1,pm2.5_cf_1_a,pm2.5_cf_1_b,pm2.5_10minute,pm2.5_10minute_a,pm2.5_10minute_b,pm2.5_30minute,pm2.5_30minute_a,pm2.5_30minute_b,pm2.5_60minute,pm2.5_60minute_a,pm2.5_60minute_b,pm2.5_6hour,pm2.5_6hour_a,pm2.5_6hour_b,pm2.5_24hour,pm2.5_24hour_a,pm2.5_24hour_b,pm2.5_1week,pm2.5_1week_a,pm2.5_1week_b,pm10.0,pm10.0_a,pm10.0_b,pm10.0_atm,pm10.0_atm_a,pm10.0_atm_b,pm10.0_cf_1,pm10.0_cf_1_a,pm10.0_cf_1_b,0.3_um_count,0.3_um_count_a,0.3_um_count_b,0.5_um_count,0.5_um_count_a,0.5_um_count_b,1.0_um_count,1.0_um_count_a,1.0_um_count_b,2.5_um_count,2.5_um_count_a,2.5_um_count_b,5.0_um_count,5.0_um_count_a,5.0_um_count_b,10.0_um_count,10.0_um_count_a,10.0_um_count_b,primary_id_a,primary_key_a,secondary_id_a,secondary_key_a,primary_id_b,primary_key_b,secondary_id_b,secondary_key_b"
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text=f"{dumps(DATA_IN_1)}",
                status_code=200,
            )
            logic_for_storing_multiple_sensors_data(padl, json_config_file)
            padl.store_sensor_data.return_value = None
            padl.store_sensor_data.side_effect = [DATA_OUT_3, DATA_OUT_4, DATA_OUT_5]
            self.assertEqual(padl.store_sensor_data.call_count, 3)

    @patch("time.sleep", return_value=None)
    def test_logic_for_storing_group_sensors_data_with_group_id_none(
        self, patched_time_sleep
    ):
        """
        Test the main logic for the PurpleAirDataLogger.`_run_loop_for_storing_group_sensors_data` method.
        """

        # Setup
        expected_url_request = "https://api.purpleair.com/v1/keys"
        padl = None
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            padl = PurpleAirDataLogger(PurpleAirApiReadKey="123456789")
            padl.store_sensor_data = MagicMock(name="store_sensor_data")
            json_config_file = {
                "sensor_group_name": "A Name Goes Here",
                "add_sensors_to_group": True,
                "sensor_index_list": [77, 81, 95079, 167897],
                "poll_interval_seconds": 60,
                "fields": "name, icon, model, hardware, location_type, private, latitude, longitude, altitude, position_rating, led_brightness, firmware_version, firmware_upgrade, rssi, uptime, pa_latency, memory, last_seen, last_modified, date_created, channel_state, channel_flags, channel_flags_manual, channel_flags_auto, confidence, confidence_manual, confidence_auto,humidity, humidity_a, humidity_b, temperature, temperature_a, temperature_b, pressure, pressure_a, pressure_b,voc, voc_a, voc_b, ozone1, analog_input,pm1.0, pm1.0_a, pm1.0_b, pm1.0_atm, pm1.0_atm_a, pm1.0_atm_b, pm1.0_cf_1, pm1.0_cf_1_a,pm1.0_cf_1_b,pm2.5_alt, pm2.5_alt_a, pm2.5_alt_b, pm2.5, pm2.5_a, pm2.5_b, pm2.5_atm, pm2.5_atm_a, pm2.5_atm_b, pm2.5_cf_1, pm2.5_cf_1_a, pm2.5_cf_1_b,pm2.5_10minute, pm2.5_10minute_a, pm2.5_10minute_b, pm2.5_30minute, pm2.5_30minute_a, pm2.5_30minute_b, pm2.5_60minute, pm2.5_60minute_a, pm2.5_60minute_b, pm2.5_6hour, pm2.5_6hour_a, pm2.5_6hour_b,pm2.5_24hour, pm2.5_24hour_a, pm2.5_24hour_b, pm2.5_1week, pm2.5_1week_a, pm2.5_1week_b,pm10.0, pm10.0_a, pm10.0_b, pm10.0_atm, pm10.0_atm_a, pm10.0_atm_b, pm10.0_cf_1, pm10.0_cf_1_a, pm10.0_cf_1_b,0.3_um_count,0.3_um_count_a,0.3_um_count_b,0.5_um_count,0.5_um_count_a,0.5_um_count_b,1.0_um_count,1.0_um_count_a,1.0_um_count_b,2.5_um_count,2.5_um_count_a,2.5_um_count_b,5.0_um_count,5.0_um_count_a,5.0_um_count_b,10.0_um_count,10.0_um_count_a,10.0_um_count_b,primary_id_a, primary_key_a, secondary_id_a, secondary_key_a, primary_id_b, primary_key_b, secondary_id_b, secondary_key_b",
                "location_type": None,
                "read_keys": None,
                "show_only": None,
                "modified_since": None,
                "max_age": None,
                "nwlng": None,
                "nwlat": None,
                "selng": None,
                "selat": None,
            }

        expected_return_data_1 = {
            "groups": [
                {"name": "A Name Goes Here!", "id": 12345},
                {"name": "A Name Goes Here!!", "id": 123456},
            ]
        }

        expected_return_data_2 = {"group_id": 1234}
        expected_return_data_3 = {}
        expected_return_data_4 = {
            "api_version": "V1.0.11-0.0.42",
            "time_stamp": 1676784867,
            "data_time_stamp": 1676784847,
            "group_id": 1234,
            "max_age": 604800,
            "firmware_default_version": "7.02",
            "fields": ["sensor_index", "name"],
            "data": [[77, "Sunnyside"], [81, "Sherwood Hills 2"]],
        }

        # Action & Expected Result
        expected_url_request_1 = "https://api.purpleair.com/v1/groups/"
        expected_url_request_2 = "https://api.purpleair.com/v1/groups"
        expected_url_request_3 = "https://api.purpleair.com/v1/groups/1234/members"
        expected_url_request_4 = "https://api.purpleair.com/v1/groups/1234/members?fields=name,icon,model,hardware,location_type,private,latitude,longitude,altitude,position_rating,led_brightness,firmware_version,firmware_upgrade,rssi,uptime,pa_latency,memory,last_seen,last_modified,date_created,channel_state,channel_flags,channel_flags_manual,channel_flags_auto,confidence,confidence_manual,confidence_auto,humidity,humidity_a,humidity_b,temperature,temperature_a,temperature_b,pressure,pressure_a,pressure_b,voc,voc_a,voc_b,ozone1,analog_input,pm1.0,pm1.0_a,pm1.0_b,pm1.0_atm,pm1.0_atm_a,pm1.0_atm_b,pm1.0_cf_1,pm1.0_cf_1_a,pm1.0_cf_1_b,pm2.5_alt,pm2.5_alt_a,pm2.5_alt_b,pm2.5,pm2.5_a,pm2.5_b,pm2.5_atm,pm2.5_atm_a,pm2.5_atm_b,pm2.5_cf_1,pm2.5_cf_1_a,pm2.5_cf_1_b,pm2.5_10minute,pm2.5_10minute_a,pm2.5_10minute_b,pm2.5_30minute,pm2.5_30minute_a,pm2.5_30minute_b,pm2.5_60minute,pm2.5_60minute_a,pm2.5_60minute_b,pm2.5_6hour,pm2.5_6hour_a,pm2.5_6hour_b,pm2.5_24hour,pm2.5_24hour_a,pm2.5_24hour_b,pm2.5_1week,pm2.5_1week_a,pm2.5_1week_b,pm10.0,pm10.0_a,pm10.0_b,pm10.0_atm,pm10.0_atm_a,pm10.0_atm_b,pm10.0_cf_1,pm10.0_cf_1_a,pm10.0_cf_1_b,0.3_um_count,0.3_um_count_a,0.3_um_count_b,0.5_um_count,0.5_um_count_a,0.5_um_count_b,1.0_um_count,1.0_um_count_a,1.0_um_count_b,2.5_um_count,2.5_um_count_a,2.5_um_count_b,5.0_um_count,5.0_um_count_a,5.0_um_count_b,10.0_um_count,10.0_um_count_a,10.0_um_count_b,primary_id_a,primary_key_a,secondary_id_a,secondary_key_a,primary_id_b,primary_key_b,secondary_id_b,secondary_key_b"

        with requests_mock.Mocker() as m1:
            m1.get(
                expected_url_request_1,
                text=f"{dumps(expected_return_data_1)}",
                status_code=200,
            )
            m1.post(
                expected_url_request_2,
                text=f"{dumps(expected_return_data_2)}",
                status_code=200,
            )
            m1.post(
                expected_url_request_3,
                text=f"{dumps(expected_return_data_3)}",
                status_code=200,
            )
            m1.get(
                expected_url_request_4,
                text=f"{dumps(expected_return_data_4)}",
                status_code=200,
            )
            self.assertEqual(
                logic_for_storing_group_sensors_data(padl, None, json_config_file), 1234
            )

    def test_logic_for_storing_group_sensors_data_without_group_id_1234(self):
        """
        Test the main logic for the PurpleAirDataLogger.`_run_loop_for_storing_group_sensors_data` method.
        """

        # Setup
        expected_url_request = "https://api.purpleair.com/v1/keys"
        padl = None
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            padl = PurpleAirDataLogger(PurpleAirApiReadKey="123456789")
            padl.store_sensor_data = MagicMock(name="store_sensor_data")
            json_config_file = {
                "sensor_group_name": "A Name Goes Here",
                "add_sensors_to_group": False,
                "sensor_index_list": [77, 81, 95079, 167897],
                "poll_interval_seconds": 60,
                "fields": "name, icon, model, hardware, location_type, rssi, uptime, pa_latency, memory, last_seen, last_modified, date_created, channel_state, confidence, confidence_manual, confidence_auto,humidity, humidity_a, humidity_b, temperature, temperature_a, temperature_b, pressure, pressure_a, pressure_b,voc, voc_a, voc_b, ozone1, analog_input,pm1.0, pm1.0_a, pm1.0_b, pm1.0_atm, pm1.0_atm_a, pm1.0_atm_b, pm1.0_cf_1, pm1.0_cf_1_a,pm1.0_cf_1_b,pm2.5_alt, pm2.5_alt_a, pm2.5_alt_b, pm2.5, pm2.5_a, pm2.5_b, pm2.5_atm, pm2.5_atm_a, pm2.5_atm_b, pm2.5_cf_1, pm2.5_cf_1_a, pm2.5_cf_1_b,pm2.5_10minute, pm2.5_10minute_a, pm2.5_10minute_b, pm2.5_30minute, pm2.5_30minute_a, pm2.5_30minute_b, pm2.5_60minute, pm2.5_60minute_a, pm2.5_60minute_b, pm2.5_6hour, pm2.5_6hour_a, pm2.5_6hour_b,pm2.5_24hour, pm2.5_24hour_a, pm2.5_24hour_b, pm2.5_1week, pm2.5_1week_a, pm2.5_1week_b,pm10.0, pm10.0_a, pm10.0_b, pm10.0_atm, pm10.0_atm_a, pm10.0_atm_b, pm10.0_cf_1, pm10.0_cf_1_a, pm10.0_cf_1_b,0.3_um_count,0.3_um_count_a,0.3_um_count_b,0.5_um_count,0.5_um_count_a,0.5_um_count_b,1.0_um_count,1.0_um_count_a,1.0_um_count_b,2.5_um_count,2.5_um_count_a,2.5_um_count_b,5.0_um_count,10.0_um_count_a,10.0_um_count_b,primary_id_a, primary_key_a, secondary_id_a, secondary_key_a, secondary_id_b, secondary_key_b",
                "location_type": None,
                "read_keys": None,
                "show_only": None,
                "modified_since": None,
                "max_age": None,
                "nwlng": None,
                "nwlat": None,
                "selng": None,
                "selat": None,
            }

        expected_return_data = {
            "api_version": "V1.0.11-0.0.42",
            "time_stamp": 1676784999,
            "data_time_stamp": 1676784999,
            "group_id": 1234,
            "max_age": 604800,
            "firmware_default_version": "7.02",
            "fields": ["sensor_index", "name"],
            "data": [[77, "Sunnyside"], [81, "Sherwood Hills 2"]],
        }

        # Action & Expected Result
        expected_url_request = "https://api.purpleair.com/v1/groups/1234/members?fields=name,icon,model,hardware,location_type,rssi,uptime,pa_latency,memory,last_seen,last_modified,date_created,channel_state,confidence,confidence_manual,confidence_auto,humidity,humidity_a,humidity_b,temperature,temperature_a,temperature_b,pressure,pressure_a,pressure_b,voc,voc_a,voc_b,ozone1,analog_input,pm1.0,pm1.0_a,pm1.0_b,pm1.0_atm,pm1.0_atm_a,pm1.0_atm_b,pm1.0_cf_1,pm1.0_cf_1_a,pm1.0_cf_1_b,pm2.5_alt,pm2.5_alt_a,pm2.5_alt_b,pm2.5,pm2.5_a,pm2.5_b,pm2.5_atm,pm2.5_atm_a,pm2.5_atm_b,pm2.5_cf_1,pm2.5_cf_1_a,pm2.5_cf_1_b,pm2.5_10minute,pm2.5_10minute_a,pm2.5_10minute_b,pm2.5_30minute,pm2.5_30minute_a,pm2.5_30minute_b,pm2.5_60minute,pm2.5_60minute_a,pm2.5_60minute_b,pm2.5_6hour,pm2.5_6hour_a,pm2.5_6hour_b,pm2.5_24hour,pm2.5_24hour_a,pm2.5_24hour_b,pm2.5_1week,pm2.5_1week_a,pm2.5_1week_b,pm10.0,pm10.0_a,pm10.0_b,pm10.0_atm,pm10.0_atm_a,pm10.0_atm_b,pm10.0_cf_1,pm10.0_cf_1_a,pm10.0_cf_1_b,0.3_um_count,0.3_um_count_a,0.3_um_count_b,0.5_um_count,0.5_um_count_a,0.5_um_count_b,1.0_um_count,1.0_um_count_a,1.0_um_count_b,2.5_um_count,2.5_um_count_a,2.5_um_count_b,5.0_um_count,10.0_um_count_a,10.0_um_count_b,primary_id_a,primary_key_a,secondary_id_a,secondary_key_a,secondary_id_b,secondary_key_b"
        with requests_mock.Mocker() as m1:
            m1.get(
                expected_url_request,
                text=f"{dumps(expected_return_data)}",
                status_code=200,
            )
            self.assertEqual(
                logic_for_storing_group_sensors_data(padl, 1234, json_config_file), 1234
            )

    def test_logic_for_storing_group_sensors_data_with_adding_group_id_4321_duplicate(
        self,
    ):
        """
        Test the main logic for the PurpleAirDataLogger.`_run_loop_for_storing_group_sensors_data` method.
        """

        # Setup
        expected_url_request = "https://api.purpleair.com/v1/keys"
        padl = None
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            padl = PurpleAirDataLogger(PurpleAirApiReadKey="123456789")
            padl.store_sensor_data = MagicMock(name="store_sensor_data")
            json_config_file = {
                "sensor_group_name": "A Name Goes Here",
                "add_sensors_to_group": True,
                "sensor_index_list": [77, 81, 95079, 167897],
                "poll_interval_seconds": 60,
                "fields": "name, icon, model, hardware, location_type, private, latitude, longitude, altitude, position_rating, led_brightness, firmware_version, firmware_upgrade, rssi, uptime, pa_latency, memory, last_seen, last_modified, date_created, channel_state, channel_flags, channel_flags_manual, channel_flags_auto, confidence, confidence_manual, confidence_auto,humidity, humidity_a, humidity_b, temperature, temperature_a, temperature_b, pressure, pressure_a, pressure_b,voc, voc_a, voc_b, ozone1, analog_input,pm1.0, pm1.0_a, pm1.0_b, pm1.0_atm, pm1.0_atm_a, pm1.0_atm_b, pm1.0_cf_1, pm1.0_cf_1_a,pm1.0_cf_1_b,pm2.5_alt, pm2.5_alt_a, pm2.5_alt_b, pm2.5, pm2.5_a, pm2.5_b, pm2.5_atm, pm2.5_atm_a, pm2.5_atm_b, pm2.5_cf_1, pm2.5_cf_1_a, pm2.5_cf_1_b,pm2.5_10minute, pm2.5_10minute_a, pm2.5_10minute_b, pm2.5_30minute, pm2.5_30minute_a, pm2.5_30minute_b, pm2.5_60minute, pm2.5_60minute_a, pm2.5_60minute_b, pm2.5_6hour, pm2.5_6hour_a, pm2.5_6hour_b,pm2.5_24hour, pm2.5_24hour_a, pm2.5_24hour_b, pm2.5_1week, pm2.5_1week_a, pm2.5_1week_b,pm10.0, pm10.0_a, pm10.0_b, pm10.0_atm, pm10.0_atm_a, pm10.0_atm_b, pm10.0_cf_1, pm10.0_cf_1_a, pm10.0_cf_1_b,0.3_um_count,0.3_um_count_a,0.3_um_count_b,0.5_um_count,0.5_um_count_a,0.5_um_count_b,1.0_um_count,1.0_um_count_a,1.0_um_count_b,2.5_um_count,2.5_um_count_a,2.5_um_count_b,5.0_um_count,5.0_um_count_a,5.0_um_count_b,10.0_um_count,10.0_um_count_a,10.0_um_count_b,primary_id_a, primary_key_a, secondary_id_a, secondary_key_a, primary_id_b, primary_key_b, secondary_id_b, secondary_key_b",
                "location_type": None,
                "read_keys": None,
                "show_only": None,
                "modified_since": None,
                "max_age": None,
                "nwlng": None,
                "nwlat": None,
                "selng": None,
                "selat": None,
            }

        expected_return_data_1 = {
            "groups": [
                {"name": "A Name Goes Here!", "id": 20},
                {"name": "A Name Goes Here", "id": 4321},
            ]
        }
        expected_return_data_2 = {}
        expected_return_data_3 = {
            "api_version": "V1.0.11-0.0.42",
            "time_stamp": 1676784867,
            "data_time_stamp": 1676784847,
            "group_id": 4321,
            "max_age": 604800,
            "firmware_default_version": "7.02",
            "fields": ["sensor_index", "name"],
            "data": [[77, "Sunnyside"], [81, "Sherwood Hills 2"]],
        }

        # Action & Expected Result
        expected_url_request_1 = "https://api.purpleair.com/v1/groups/"
        expected_url_request_2 = "https://api.purpleair.com/v1/groups/4321/members"
        expected_url_request_3 = "https://api.purpleair.com/v1/groups/4321/members?fields=name,icon,model,hardware,location_type,private,latitude,longitude,altitude,position_rating,led_brightness,firmware_version,firmware_upgrade,rssi,uptime,pa_latency,memory,last_seen,last_modified,date_created,channel_state,channel_flags,channel_flags_manual,channel_flags_auto,confidence,confidence_manual,confidence_auto,humidity,humidity_a,humidity_b,temperature,temperature_a,temperature_b,pressure,pressure_a,pressure_b,voc,voc_a,voc_b,ozone1,analog_input,pm1.0,pm1.0_a,pm1.0_b,pm1.0_atm,pm1.0_atm_a,pm1.0_atm_b,pm1.0_cf_1,pm1.0_cf_1_a,pm1.0_cf_1_b,pm2.5_alt,pm2.5_alt_a,pm2.5_alt_b,pm2.5,pm2.5_a,pm2.5_b,pm2.5_atm,pm2.5_atm_a,pm2.5_atm_b,pm2.5_cf_1,pm2.5_cf_1_a,pm2.5_cf_1_b,pm2.5_10minute,pm2.5_10minute_a,pm2.5_10minute_b,pm2.5_30minute,pm2.5_30minute_a,pm2.5_30minute_b,pm2.5_60minute,pm2.5_60minute_a,pm2.5_60minute_b,pm2.5_6hour,pm2.5_6hour_a,pm2.5_6hour_b,pm2.5_24hour,pm2.5_24hour_a,pm2.5_24hour_b,pm2.5_1week,pm2.5_1week_a,pm2.5_1week_b,pm10.0,pm10.0_a,pm10.0_b,pm10.0_atm,pm10.0_atm_a,pm10.0_atm_b,pm10.0_cf_1,pm10.0_cf_1_a,pm10.0_cf_1_b,0.3_um_count,0.3_um_count_a,0.3_um_count_b,0.5_um_count,0.5_um_count_a,0.5_um_count_b,1.0_um_count,1.0_um_count_a,1.0_um_count_b,2.5_um_count,2.5_um_count_a,2.5_um_count_b,5.0_um_count,5.0_um_count_a,5.0_um_count_b,10.0_um_count,10.0_um_count_a,10.0_um_count_b,primary_id_a,primary_key_a,secondary_id_a,secondary_key_a,primary_id_b,primary_key_b,secondary_id_b,secondary_key_b"

        with requests_mock.Mocker() as m1:
            m1.get(
                expected_url_request_1,
                text=f"{dumps(expected_return_data_1)}",
                status_code=200,
            )
            m1.post(
                expected_url_request_2,
                text=f"{dumps(expected_return_data_2)}",
                status_code=200,
            )
            m1.get(
                expected_url_request_3,
                text=f"{dumps(expected_return_data_3)}",
                status_code=200,
            )
            self.assertEqual(
                logic_for_storing_group_sensors_data(padl, None, json_config_file), 4321
            )

    def test_logic_for_storing_group_sensors_data_with_adding_group_id_4567_duplicate_and_members_duplicate(
        self,
    ):
        """
        Test the main logic for the PurpleAirDataLogger.`_run_loop_for_storing_group_sensors_data` method.
        """

        # Setup
        expected_url_request = "https://api.purpleair.com/v1/keys"
        padl = None
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                text='{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                status_code=200,
            )
            padl = PurpleAirDataLogger(PurpleAirApiReadKey="123456789")
            padl.store_sensor_data = MagicMock(name="store_sensor_data")
            json_config_file = {
                "sensor_group_name": "A Name Goes Here",
                "add_sensors_to_group": True,
                "sensor_index_list": [77, 81, 95079, 167897],
                "poll_interval_seconds": 60,
                "fields": "name, fields",
                "location_type": None,
                "read_keys": None,
                "show_only": None,
                "modified_since": None,
                "max_age": None,
                "nwlng": None,
                "nwlat": None,
                "selng": None,
                "selat": None,
            }

        expected_return_data_1 = {
            "groups": [
                {"name": "A Name Goes Here!", "id": 20},
                {"name": "A Name Goes Here", "id": 4567},
            ]
        }
        expected_return_data_2 = {
            "error": 4567,
            "description": "409: DuplicateGroupEntryError - This sensor already exists in this group.",
        }

        expected_return_data_3 = {
            "api_version": "V1.0.11-0.0.42",
            "time_stamp": 1676784867,
            "data_time_stamp": 1676784847,
            "group_id": 4567,
            "max_age": 604800,
            "firmware_default_version": "7.02",
            "fields": ["sensor_index", "name"],
            "data": [[77, "Sunnyside"], [81, "Sherwood Hills 2"]],
        }

        # Action & Expected Result
        expected_url_request_1 = "https://api.purpleair.com/v1/groups/"
        expected_url_request_2 = "https://api.purpleair.com/v1/groups/4567/members"
        expected_url_request_3 = (
            "https://api.purpleair.com/v1/groups/4567/members?fields=name,fields"
        )

        with requests_mock.Mocker() as m1:
            m1.get(
                expected_url_request_1,
                text=f"{dumps(expected_return_data_1)}",
                status_code=200,
            )
            m1.post(
                expected_url_request_2,
                text=f"{dumps(expected_return_data_2)}",
                status_code=409,
            )
            m1.get(
                expected_url_request_3,
                text=f"{dumps(expected_return_data_3)}",
                status_code=200,
            )
            self.assertEqual(
                logic_for_storing_group_sensors_data(padl, None, json_config_file), 4567
            )

    def test_logic_for_storing_local_sensors_data(self):
        """
        Test the main logic for the PurpleAirDataLogger.`_run_loop_for_storing_local_sensors_data` method.
        """

        test_data_in = [LOCAL_API_DATA_IN_1, LOCAL_API_DATA_IN_2]
        test_data_out = [LOCAL_API_DATA_OUT_1, LOCAL_API_DATA_OUT_2]
        for (
            index,
            test_data,
        ) in enumerate(test_data_in):
            # Setup
            expected_url_request = "http://192.168.1.2/json"
            padl = None
            with requests_mock.Mocker() as m:
                m.get(
                    expected_url_request,
                    text="{}",
                    status_code=200,
                )
                padl = PurpleAirDataLogger(PurpleAirApiIpv4Address=["192.168.1.2"])
                padl.store_sensor_data = MagicMock(name="store_sensor_data")
            json_config_file = {
                "sensor_ip_list": ["192.168.1.2"],
                "poll_interval_seconds": 1,
            }

            # Action & Expected Result
            expected_url_request = "http://192.168.1.2/json"

            with requests_mock.Mocker() as m:
                m.get(
                    expected_url_request,
                    text=f"{dumps(test_data)}",
                    status_code=200,
                )
                logic_for_storing_local_sensors_data(padl, json_config_file)
                padl.store_sensor_data.return_value = None
                padl.store_sensor_data.assert_called_once_with(test_data_out[index])
