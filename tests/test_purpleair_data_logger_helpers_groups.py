#!/usr/bin/env python3

"""
Copyright 2023 carlkidcrypto, All rights reserved.

Unit tests for PurpleAirDataLoggerHelpers group sensors data storage logic.
"""

from json import dumps
import sys
import unittest
from unittest.mock import MagicMock, patch

import requests_mock

sys.path.append("../")

from purpleair_api.PurpleAirAPIError import PurpleAirAPIError
from purpleair_data_logger.PurpleAirDataLogger import PurpleAirDataLogger
from purpleair_data_logger.PurpleAirDataLoggerHelpers import (
    logic_for_storing_group_sensors_data,
)


class PurpleAirDataLoggerHelpersGroupsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

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
                [
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                        "status_code": 200,
                    },
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "WRITE"}',
                        "status_code": 200,
                    },
                ],
            )
            padl = PurpleAirDataLogger(
                PurpleAirApiReadKey="123456789", PurpleAirApiWriteKey="write-key-789"
            )
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
                [
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                        "status_code": 200,
                    },
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "WRITE"}',
                        "status_code": 200,
                    },
                ],
            )
            padl = PurpleAirDataLogger(
                PurpleAirApiReadKey="123456789", PurpleAirApiWriteKey="write-key-789"
            )
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
                [
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                        "status_code": 200,
                    },
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "WRITE"}',
                        "status_code": 200,
                    },
                ],
            )
            padl = PurpleAirDataLogger(
                PurpleAirApiReadKey="123456789", PurpleAirApiWriteKey="write-key-789"
            )
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
                [
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                        "status_code": 200,
                    },
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "WRITE"}',
                        "status_code": 200,
                    },
                ],
            )
            padl = PurpleAirDataLogger(
                PurpleAirApiReadKey="123456789", PurpleAirApiWriteKey="write-key-789"
            )
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

    def test_logic_for_storing_group_sensors_data_with_add_sensors_false(self):
        """
        Test the branch where add_sensors_to_group is False — sensors should NOT be added.
        """

        expected_url_request = "https://api.purpleair.com/v1/keys"
        padl = None
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                [
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                        "status_code": 200,
                    },
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "WRITE"}',
                        "status_code": 200,
                    },
                ],
            )
            padl = PurpleAirDataLogger(
                PurpleAirApiReadKey="123456789", PurpleAirApiWriteKey="write-key-789"
            )
            padl.store_sensor_data = MagicMock(name="store_sensor_data")
            json_config_file = {
                "sensor_group_name": "A Name Goes Here",
                "add_sensors_to_group": False,
                "sensor_index_list": [77],
                "poll_interval_seconds": 60,
                "fields": "name",
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

        expected_groups = {"groups": [{"name": "A Name Goes Here", "id": 9999}]}
        expected_members_data = {
            "api_version": "V1.0.11-0.0.42",
            "time_stamp": 1676784867,
            "data_time_stamp": 1676784847,
            "group_id": 9999,
            "max_age": 604800,
            "firmware_default_version": "7.02",
            "fields": ["sensor_index", "name"],
            "data": [[77, "Sunnyside"]],
        }

        with requests_mock.Mocker() as m1:
            m1.get(
                "https://api.purpleair.com/v1/groups/",
                text=f"{dumps(expected_groups)}",
                status_code=200,
            )
            m1.get(
                "https://api.purpleair.com/v1/groups/9999/members?fields=name",
                text=f"{dumps(expected_members_data)}",
                status_code=200,
            )
            result = logic_for_storing_group_sensors_data(padl, None, json_config_file)
            self.assertEqual(result, 9999)

    def test_logic_for_storing_group_sensors_data_reraises_non_duplicate_error(self):
        """
        Test that a non-duplicate PurpleAirAPIError is re-raised when adding sensors.
        """
        expected_url_request = "https://api.purpleair.com/v1/keys"
        padl = None
        with requests_mock.Mocker() as m:
            m.get(
                expected_url_request,
                [
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "READ"}',
                        "status_code": 200,
                    },
                    {
                        "text": '{"api_version" : "1.1.1", "time_stamp": 123456789, "api_key_type": "WRITE"}',
                        "status_code": 200,
                    },
                ],
            )
            padl = PurpleAirDataLogger(
                PurpleAirApiReadKey="123456789", PurpleAirApiWriteKey="write-key-789"
            )
            padl.store_sensor_data = MagicMock(name="store_sensor_data")
            json_config_file = {
                "sensor_group_name": "A Name Goes Here",
                "add_sensors_to_group": True,
                "sensor_index_list": [77],
                "poll_interval_seconds": 60,
                "fields": "name",
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

        expected_groups = {"groups": [{"name": "A Name Goes Here", "id": 8888}]}
        non_duplicate_error_response = {
            "error": 403,
            "description": "403: Forbidden - Access denied.",
        }

        with requests_mock.Mocker() as m1:
            m1.get(
                "https://api.purpleair.com/v1/groups/",
                text=f"{dumps(expected_groups)}",
                status_code=200,
            )
            m1.post(
                "https://api.purpleair.com/v1/groups/8888/members",
                text=f"{dumps(non_duplicate_error_response)}",
                status_code=403,
            )
            with self.assertRaises(PurpleAirAPIError):
                logic_for_storing_group_sensors_data(padl, None, json_config_file)


if __name__ == "__main__":
    unittest.main()
