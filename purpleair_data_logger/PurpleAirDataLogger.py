#!/usr/bin/env python3

"""
    Copyright 2023 carlkidcrypto, All rights reserved.
    A python base Data Logger class.
"""

from purpleair_api.PurpleAirAPI import PurpleAirAPI, debug_log, PurpleAirAPIError
from purpleair_api.PurpleAirAPIConstants import ACCEPTED_FIELD_NAMES_DICT
from time import sleep
import json
import argparse


def generate_common_arg_parser(argparse_description=""):
    """
    A function to generate the common arguments that all data loggers need

    :param str argparse_description: A description for the argument parser that will be return

    :return An instance of argparse with the common arguments added.
    """

    parser = argparse.ArgumentParser(description=argparse_description)

    parser.add_argument(
        "-paa_read_key",
        required=False,
        default=None,
        dest="paa_read_key",
        type=str,
        help="""The PurpleAirAPI Read key""",
    )

    parser.add_argument(
        "-paa_write_key",
        required=False,
        default=None,
        dest="paa_write_key",
        type=str,
        help="""The PurpleAirAPI write key""",
    )

    parser.add_argument(
        "-paa_single_sensor_request_json_file",
        required=False,
        default=None,
        dest="paa_single_sensor_request_json_file",
        type=str,
        help="""The
                            path to a json file containing the parameters to send a single
                            sensor request.""",
    )

    parser.add_argument(
        "-paa_multiple_sensor_request_json_file",
        required=False,
        default=None,
        dest="paa_multiple_sensor_request_json_file",
        type=str,
        help="""The
                            path to a json file containing the parameters to send a multiple
                            sensor request.""",
    )

    parser.add_argument(
        "-paa_group_sensor_request_json_file",
        required=False,
        default=None,
        dest="paa_group_sensor_request_json_file",
        type=str,
        help="""The
                            path to a json file containing the parameters to send a group
                            sensor request.""",
    )

    parser.add_argument(
        "-paa_local_sensor_request_json_file",
        required=False,
        default=None,
        dest="paa_local_sensor_request_json_file",
        type=str,
        help="""The
                            path to a json file containing the parameters to send a local
                            sensor request.""",
    )

    return parser


class PurpleAirDataLoggerError(Exception):
    """
    Custom Exception for our PurpleAirDataLogger class.
    """

    def __init__(self, message_string):
        self.message = message_string
        super().__init__(self.message)


class PurpleAirDataLogger:
    """
    The Base Data Logger class. Will define common methods used by other data loggers. For
    example, PSQLDataLogger, CSVDataLogger, or SQLiteDataLogger. Inheritors of this class
    will only need to define their own 'store_sensor_data' method.
    """

    def __init__(
        self,
        PurpleAirApiReadKey=None,
        PurpleAirApiWriteKey=None,
        PurpleAirApiIpv4Address=None,
    ):
        """
        :param str PurpleAirApiReadKey: A valid PurpleAirAPI Read key
        :param object psql_db_conn: A valid PG8000 database connection
        """

        # Make one instance of our PurpleAirAPI class
        self._purpleair_api_obj = PurpleAirAPI(
            your_api_read_key=PurpleAirApiReadKey,
            your_api_write_key=PurpleAirApiWriteKey,
            your_ipv4_address=PurpleAirApiIpv4Address,
        )

        # Define how often we send requests
        self._send_request_every_x_seconds = 65

    @property
    def send_request_every_x_seconds(self):
        """
        Return the current value of send_request_every_x_seconds.
        This value is how often we send requests to the Purple Air API. (PAA)
        """

        return self._send_request_every_x_seconds

    @send_request_every_x_seconds.setter
    def send_request_every_x_seconds(self, new_value):
        """
        Set the current value of send_request_every_x_seconds.
        This value is how often we send requests to the Purple Air API. (PAA)
        Value shall be greater than or equal to 60. The value is in seconds.
        """

        if new_value >= 60:
            self._send_request_every_x_seconds = new_value

        else:
            raise PurpleAirDataLoggerError(
                f"new_value ({new_value}) shall not be less than 60."
            )

    def store_sensor_data(self, single_sensor_data_dict):
        """
        Insert the sensor data into the database.

        :param dict single_sensor_data_dict: A python dictionary containing all fields
                                             for insertion. If a sensor doesn't support
                                             a certain field make sure it is NULL and part
                                             of the dictionary. This method does no type
                                             or error checking. That is upto the caller.
        """

        raise NotImplementedError(
            "Must be implemented by class that is inheriting PurpleAirDataLogger!"
        )

    def _validate_sensor_data_before_insert(self, the_modified_sensor_data) -> dict:
        """
        Before we store the data, we must make sure all fields have been included.
        Our psql/sqlite store statements expect all fields regardless of what we request.

        :param dict the_modified_sensor_data: A single layer dictionary containing a single sensors data.

        return A dictionary with all the data fields filled out.
        """

        # Make a copy first
        temp_the_modified_sensor_data = the_modified_sensor_data
        for field in ACCEPTED_FIELD_NAMES_DICT.keys():
            if field not in temp_the_modified_sensor_data.keys():
                temp_the_modified_sensor_data[str(field)] = ACCEPTED_FIELD_NAMES_DICT[
                    field
                ]

        # Delete some stuff
        del the_modified_sensor_data

        # Then return the modified copy
        return temp_the_modified_sensor_data

    def _run_loop_for_storing_single_sensor_data(self, json_config_file) -> dict:
        """
        A method containing the run loop for inserting a single sensors' data into the data logger.

        :param dict json_config_file: A dictionary object of the json config file using json load.
        """

        # Set the polling interval
        self.send_request_every_x_seconds = json_config_file["poll_interval_seconds"]

        while True:
            print(
                "_run_loop_for_storing_single_sensor_data - Beep boop I am alive...\n\n"
            )
            # We will request data once every 65 seconds.
            debug_log(
                f"""Requesting new data from a sensor with index
                      {json_config_file['sensor_index']}..."""
            )

            sensor_data = None
            sensor_data = self._purpleair_api_obj.request_sensor_data(
                json_config_file["sensor_index"],
                json_config_file["read_key"],
                json_config_file["fields"],
            )

            # Let's make it easier on ourselves by making the sensor data one level deep.
            # Instead of json["sensor"]["KEYS..."] and json["sensor"]["stats_a"]["KEYS..."] etc
            # We turn it into just json["KEYS..."].
            the_modified_sensor_data = {}
            the_modified_sensor_data["data_time_stamp"] = sensor_data["data_time_stamp"]
            for key, val in sensor_data["sensor"].items():
                if key == "stats":
                    # For now name this one stats_pm2.5 until I understand the difference
                    # between sensor_data["stats"]["pm2.5"] and sensor_data["pm2.5"].
                    # Update 07/25/2022: Heard back from PurpleAir. They are the same.
                    the_modified_sensor_data["stats_pm2.5"] = val["pm2.5"]
                    the_modified_sensor_data["pm2.5_10minute"] = val["pm2.5_10minute"]
                    the_modified_sensor_data["pm2.5_30minute"] = val["pm2.5_30minute"]
                    the_modified_sensor_data["pm2.5_60minute"] = val["pm2.5_60minute"]
                    the_modified_sensor_data["pm2.5_6hour"] = val["pm2.5_6hour"]
                    the_modified_sensor_data["pm2.5_24hour"] = val["pm2.5_24hour"]
                    the_modified_sensor_data["pm2.5_1week"] = val["pm2.5_1week"]
                    the_modified_sensor_data["pm2.5_time_stamp"] = val["time_stamp"]

                elif key in ["stats_a", "stats_b"]:
                    the_modified_sensor_data[f"pm2.5_{key[-1]}"] = val["pm2.5"]
                    the_modified_sensor_data[f"pm2.5_10minute_{key[-1]}"] = val[
                        "pm2.5_10minute"
                    ]
                    the_modified_sensor_data[f"pm2.5_30minute_{key[-1]}"] = val[
                        "pm2.5_30minute"
                    ]
                    the_modified_sensor_data[f"pm2.5_60minute_{key[-1]}"] = val[
                        "pm2.5_60minute"
                    ]
                    the_modified_sensor_data[f"pm2.5_6hour_{key[-1]}"] = val[
                        "pm2.5_6hour"
                    ]
                    the_modified_sensor_data[f"pm2.5_24hour_{key[-1]}"] = val[
                        "pm2.5_24hour"
                    ]
                    the_modified_sensor_data[f"pm2.5_1week_{key[-1]}"] = val[
                        "pm2.5_1week"
                    ]
                    the_modified_sensor_data[f"time_stamp_{key[-1]}"] = val[
                        "time_stamp"
                    ]

                else:
                    the_modified_sensor_data[key] = val

            the_modified_sensor_data = self._validate_sensor_data_before_insert(
                the_modified_sensor_data
            )
            self.store_sensor_data(the_modified_sensor_data)
            debug_log(
                f"""Waiting {self.send_request_every_x_seconds} seconds before
                  requesting new data again..."""
            )

            # Delete some stuff
            del sensor_data
            del the_modified_sensor_data

            sleep(self.send_request_every_x_seconds)

    def _run_loop_for_storing_multiple_sensors_data(self, json_config_file) -> dict:
        """
        A method containing the run loop for inserting a multiple sensors' data into the data logger.

        :param dict json_config_file: A dictionary object of the json config file using json load.
        """

        # Set the polling interval
        self.send_request_every_x_seconds = json_config_file["poll_interval_seconds"]

        while True:
            print(
                "_run_loop_for_storing_multiple_sensors_data - Beep boop I am alive...\n\n"
            )
            # We will request data once every 65 seconds.
            debug_log(
                f"""Requesting new data from multiple sensors with fields
                      {json_config_file["fields"]}..."""
            )

            sensors_data = None
            sensors_data = self._purpleair_api_obj.request_multiple_sensors_data(
                fields=json_config_file["fields"],
                location_type=json_config_file["location_type"],
                read_keys=json_config_file["read_keys"],
                show_only=json_config_file["show_only"],
                modified_since=json_config_file["modified_since"],
                max_age=json_config_file["max_age"],
                nwlng=json_config_file["nwlng"],
                nwlat=json_config_file["nwlat"],
                selng=json_config_file["selng"],
                selat=json_config_file["selat"],
            )

            # The sensors data will look something like this:
            # {'api_version': 'V1.0.11-0.0.34', 'time_stamp': 1659710288, 'data_time_stamp': 1659710232,
            # 'max_age': 604800, 'firmware_default_version': '7.00', 'fields': ['sensor_index', 'name'],
            # 'data': [[131075, 'Mariners Bluff'], [131079, 'BRSKBV-outside'], [131077, 'BEE Patio'],
            # ... ]}
            # It is important to know that the order of 'fields' provided as an argument to request_multiple_sensors_data()
            # will determine the order of data items. In a nutshell it is a 1:1 mapping from fields to data.
            # Now lets build and feed what the store_sensor_data() method expects.
            store_sensor_data_type_list = []
            store_sensor_data_type_list = self._construct_store_sensor_data_type(
                sensors_data
            )

            for store_sensor_data_type in store_sensor_data_type_list:
                # Store the current data
                self.store_sensor_data(store_sensor_data_type)

            debug_log(
                f"""Waiting {self.send_request_every_x_seconds} seconds before
                  requesting new data again..."""
            )

            # Delete some stuff
            del sensors_data
            del store_sensor_data_type_list

            sleep(self.send_request_every_x_seconds)

    def _run_loop_for_storing_group_sensors_data(self, json_config_file) -> dict:
        """
        A method containing the run loop for inserting a group sensors' data into the data logger.

        :param dict json_config_file: A dictionary object of the json config file using json load.
        """

        # Set the polling interval
        self.send_request_every_x_seconds = json_config_file["poll_interval_seconds"]

        group_id_to_use = None
        while True:
            print(
                "_run_loop_for_storing_group_sensors_data - Beep boop I am alive...\n\n"
            )

            if group_id_to_use is None:
                # Get a current list of sensors that the API key provided owns
                group_dict_list_data = (
                    self._purpleair_api_obj.request_group_list_data()["groups"]
                )

                # Now make the sensor_group_name if it doesn't already exist.
                does_sensor_group_name_exist = False
                for item in group_dict_list_data:
                    name = item["name"]
                    id = item["id"]
                    # Find the first name that matches our sensor_group_name. No use to continue further
                    if bool(name == json_config_file["sensor_group_name"]):
                        does_sensor_group_name_exist = True
                        group_id_to_use = id
                        break

                if bool(does_sensor_group_name_exist == False):
                    print(
                        f"Your provided `sensor_group_name` - `{json_config_file['sensor_group_name']}` doesn't exist. A new one will be created..."
                    )
                    retval = self._purpleair_api_obj.post_create_group_data(
                        json_config_file["sensor_group_name"]
                    )
                    group_id_to_use = retval["group_id"]
                    print(
                        f"Your provided `sensor_group_name` - `{json_config_file['sensor_group_name']}` has been created! Its `group_id` number is `{group_id_to_use}`..."
                    )
                    print(
                        f"Waiting {self.send_request_every_x_seconds} seconds for group to be created on server..."
                    )
                    sleep(self.send_request_every_x_seconds)

                else:
                    print(
                        f"Your provided `sensor_group_name` - `{json_config_file['sensor_group_name']}` already exists. A new one will not be created..."
                    )

                # By now we have a group_id_to_use. Let see if the user wants us to add members
                if bool(json_config_file["add_sensors_to_group"]):
                    print(
                        f"Attempting to add the sensors in `sensor_index_list` to the `group_id` - {group_id_to_use}..."
                    )
                    for sensor_index_val in json_config_file["sensor_index_list"]:
                        try:
                            retval = self._purpleair_api_obj.post_create_member(
                                group_id=group_id_to_use, sensor_index=sensor_index_val
                            )
                            print(
                                f"`sensor_index` - {sensor_index_val} successfully added to group..."
                            )

                        except PurpleAirAPIError as err:
                            if (
                                "409: DuplicateGroupEntryError - This sensor already exists in this group."
                                in err.message
                            ):
                                print(
                                    f"`sensor_index` - {sensor_index_val} already exists in group..."
                                )

                            else:
                                raise err

                else:
                    print(
                        f"No sensors will be added to the `group_id` - {group_id_to_use}..."
                    )

            assert group_id_to_use is not None
            members_data = self._purpleair_api_obj.request_members_data(
                group_id=group_id_to_use,
                fields=json_config_file["fields"],
                location_type=json_config_file["location_type"],
                read_keys=json_config_file["read_keys"],
                show_only=json_config_file["show_only"],
                modified_since=json_config_file["modified_since"],
                max_age=json_config_file["max_age"],
                nwlng=json_config_file["nwlng"],
                nwlat=json_config_file["nwlat"],
                selng=json_config_file["selng"],
                selat=json_config_file["selat"],
            )

            assert group_id_to_use == members_data["group_id"]
            # The sensors data will look something like this:
            # {'api_version': 'V1.0.11-0.0.42', 'time_stamp': 1676784867, 'data_time_stamp': 1676784847, 'group_id': 1654,
            # 'max_age': 604800, 'firmware_default_version': '7.02', 'fields': ['sensor_index', 'name'], 'data': [[77, 'Sunnyside'],
            # [81, 'Sherwood Hills 2']]}
            # It is important to know that the order of 'fields' provided as an argument to request_multiple_sensors_data()
            # will determine the order of data items. In a nutshell it is a 1:1 mapping from fields to data.
            # Now lets build and feed what the store_sensor_data() method expects.

            store_sensor_data_type_list = self._construct_store_sensor_data_type(
                members_data
            )

            for store_sensor_data_type in store_sensor_data_type_list:
                # Store the current data
                self.store_sensor_data(store_sensor_data_type)

            debug_log(
                f"""Waiting {self.send_request_every_x_seconds} seconds before
                  requesting new data again..."""
            )

            sleep(self.send_request_every_x_seconds)

    def _run_loop_for_storing_local_sensors_data(self, json_config_file) -> dict:
        """
        A method containing the run loop for inserting a local sensors' data into the data logger.

        :param dict json_config_file: A dictionary object of the json config file using json load.
        """

        while True:
            print(
                "_run_loop_for_storing_local_sensors_data - Beep boop I am alive...\n\n"
            )

            # Ask for our local sensor data
            local_sensor_dict = self._purpleair_api_obj.request_local_sensor_data()

            # The data that is returned via an internal network API is different than the data returned via an external network API.
            # With that in mind let's try to map internal network API values to external network API values. That way we don't have to
            # write more code in the PADL's.
            for ip, sensor_dict in local_sensor_dict.items():
                the_modified_sensor_data = {}

                # This timestamp appears to be a unix epoch timestamp (seconds) type.
                the_modified_sensor_data["data_time_stamp"] = sensor_dict[
                    "response_date"
                ]

                # Since we want this to work for all loggers let's make an assumption. The 'SensorId' is the 'name' since it is just a MAC address.
                # The 'Id' is not the `sensor_index` it increments when the data changes. It is more of a `sample_id`. Let's just use the mac as a base
                # 10 number. That should be unique.
                the_modified_sensor_data["sensor_index"] = int(
                    str(sensor_dict["SensorId"]).replace(":", ""), 16
                )

                ###### Station information and status fields: ######
                the_modified_sensor_data["name"] = sensor_dict["SensorId"]
                # "icon": 0,
                # "model": "",
                the_modified_sensor_data["hardware"] = sensor_dict["hardwarediscovered"]
                if sensor_dict["place"] == "inside":
                    the_modified_sensor_data["location_type"] = 1

                elif sensor_dict["place"] == "outside":
                    the_modified_sensor_data["location_type"] = 0

                # "private": 0,
                the_modified_sensor_data["latitude"] = sensor_dict["lat"]
                the_modified_sensor_data["longitude"] = sensor_dict["lon"]
                # "altitude": 0.0,
                # "position_rating": 0,
                # "led_brightness": 0,
                the_modified_sensor_data["firmware_version"] = sensor_dict["version"]
                # "firmware_upgrade": "",
                the_modified_sensor_data["rssi"] = sensor_dict["rssi"]
                the_modified_sensor_data["uptime"] = sensor_dict["uptime"]
                the_modified_sensor_data["pa_latency"] = sensor_dict["latency"]
                # "last_seen": 0,
                # "last_modified": 0,
                # "date_created": 0,
                # "channel_state": 0,
                # "channel_flags": 0,
                # "channel_flags_manual": 0,
                # "channel_flags_auto": 0,
                # "confidence": 0,
                # "confidence_manual": 0,
                # "confidence_auto": 0,

                ###### Environmental fields: ######
                if "current_humidity_680" not in sensor_dict.keys():
                    the_modified_sensor_data["humidity"] = sensor_dict[
                        "current_humidity"
                    ]
                    the_modified_sensor_data["humidity_a"] = sensor_dict[
                        "current_humidity"
                    ]

                else:
                    the_modified_sensor_data["humidity_a"] = sensor_dict[
                        "current_humidity"
                    ]
                    the_modified_sensor_data["humidity_b"] = sensor_dict[
                        "current_humidity_680"
                    ]
                    the_modified_sensor_data["humidity"] = float(
                        (
                            sensor_dict["current_humidity"]
                            + sensor_dict["current_humidity_680"]
                        )
                        / 2
                    )

                if "current_temp_f_680" not in sensor_dict.keys():
                    the_modified_sensor_data["temperature"] = sensor_dict[
                        "current_temp_f"
                    ]
                    the_modified_sensor_data["temperature_a"] = sensor_dict[
                        "current_temp_f"
                    ]

                else:
                    the_modified_sensor_data["temperature_a"] = sensor_dict[
                        "current_temp_f"
                    ]
                    the_modified_sensor_data["temperature_b"] = sensor_dict[
                        "current_temp_f_680"
                    ]
                    the_modified_sensor_data["temperature"] = float(
                        (
                            sensor_dict["current_temp_f"]
                            + sensor_dict["current_temp_f_680"]
                        )
                        / 2
                    )

                if "pressure_680" not in sensor_dict.keys():
                    the_modified_sensor_data["pressure"] = sensor_dict["pressure"]
                    the_modified_sensor_data["pressure_a"] = sensor_dict["pressure"]

                else:
                    the_modified_sensor_data["pressure_a"] = sensor_dict["pressure"]
                    the_modified_sensor_data["pressure_b"] = sensor_dict["pressure_680"]
                    the_modified_sensor_data["pressure"] = float(
                        (sensor_dict["pressure"] + sensor_dict["pressure_680"]) / 2
                    )

                ###### Miscellaneous fields: ######
                # "voc": 0.0,
                # "voc_a": 0.0,
                # "voc_b": 0.0,
                # "ozone1": 0.0,
                # "analog_input": 0.0,

                ###### PM1.0 fields: ######
                if "p_1_0_um_b" not in sensor_dict.keys():
                    the_modified_sensor_data["pm1.0"] = sensor_dict["p_1_0_um"]
                    the_modified_sensor_data["pm1.0_a"] = sensor_dict["p_1_0_um"]

                else:
                    the_modified_sensor_data["pm1.0"] = float(
                        (sensor_dict["p_1_0_um"] + sensor_dict["p_1_0_um_b"]) / 2
                    )
                    the_modified_sensor_data["pm1.0_a"] = sensor_dict["p_1_0_um"]
                    the_modified_sensor_data["pm1.0_b"] = sensor_dict["p_1_0_um_b"]

                if "pm1_0_atm_b" not in sensor_dict.keys():
                    the_modified_sensor_data["pm1.0_atm"] = sensor_dict["pm1_0_atm"]
                    the_modified_sensor_data["pm1.0_atm_a"] = sensor_dict["pm1_0_atm"]

                else:
                    the_modified_sensor_data["pm1.0_atm"] = float(
                        (sensor_dict["pm1_0_atm"] + sensor_dict["pm1_0_atm_b"]) / 2
                    )
                    the_modified_sensor_data["pm1.0_atm_a"] = sensor_dict["pm1_0_atm"]
                    the_modified_sensor_data["pm1.0_atm_b"] = sensor_dict["pm1_0_atm_b"]

                if "pm1_0_cf_1_b" not in sensor_dict.keys():
                    the_modified_sensor_data["pm1.0_cf_1"] = sensor_dict["pm1_0_cf_1"]
                    the_modified_sensor_data["pm1.0_cf_1_a"] = sensor_dict["pm1_0_cf_1"]

                else:
                    the_modified_sensor_data["pm1.0_cf_1"] = float(
                        (sensor_dict["pm1_0_cf_1"] + sensor_dict["pm1_0_cf_1_b"]) / 2
                    )
                    the_modified_sensor_data["pm1.0_cf_1_a"] = sensor_dict["pm1_0_cf_1"]
                    the_modified_sensor_data["pm1.0_cf_1_b"] = sensor_dict[
                        "pm1_0_cf_1_b"
                    ]

                ###### PM2.5 fields: ######
                # "pm2.5_alt": 0.0,
                # "pm2.5_alt_a": 0.0,
                # "pm2.5_alt_b": 0.0,
                if "p_2_5_um_b" not in sensor_dict.keys():
                    the_modified_sensor_data["pm2.5"] = sensor_dict["p_2_5_um"]
                    the_modified_sensor_data["pm2.5_a"] = sensor_dict["p_2_5_um"]

                else:
                    the_modified_sensor_data["pm2.5"] = float(
                        (sensor_dict["p_2_5_um"] + sensor_dict["p_2_5_um_b"]) / 2
                    )
                    the_modified_sensor_data["pm2.5_a"] = sensor_dict["p_2_5_um"]
                    the_modified_sensor_data["pm2.5_b"] = sensor_dict["p_2_5_um_b"]

                if "pm2_5_atm_b" not in sensor_dict.keys():
                    the_modified_sensor_data["pm2.5_atm"] = sensor_dict["pm2_5_atm"]
                    the_modified_sensor_data["pm2.5_atm_a"] = sensor_dict["pm2_5_atm"]

                else:
                    the_modified_sensor_data["pm2.5_atm"] = float(
                        (sensor_dict["pm2_5_atm"] + sensor_dict["pm2_5_atm_b"]) / 2
                    )
                    the_modified_sensor_data["pm2.5_atm_a"] = sensor_dict["pm2_5_atm"]
                    the_modified_sensor_data["pm2.5_atm_b"] = sensor_dict["pm2_5_atm_b"]

                if "pm2_5_cf_1_b" not in sensor_dict.keys():
                    the_modified_sensor_data["pm2.5_cf_1"] = sensor_dict["pm2_5_cf_1"]
                    the_modified_sensor_data["pm2.5_cf_1_a"] = sensor_dict["pm2_5_cf_1"]

                else:
                    the_modified_sensor_data["pm2.5_cf_1"] = float(
                        (sensor_dict["pm2_5_cf_1"] + sensor_dict["pm2_5_cf_1_b"]) / 2
                    )
                    the_modified_sensor_data["pm2.5_cf_1_a"] = sensor_dict["pm2_5_cf_1"]
                    the_modified_sensor_data["pm2.5_cf_1_b"] = sensor_dict[
                        "pm2_5_cf_1_b"
                    ]

                # # PM2.5 pseudo (simple running) average fields:
                # # Note: These are inside the return json as json["sensor"]["stats"]. They are averages of the two sensors.
                # # sensor 'a' and sensor 'b'. Each sensors data is inside json["sensor"]["stats_a"] and json["sensor"]["stats_b"]
                # "pm2.5_10minute": 0.0,
                # "pm2.5_10minute_a": 0.0,
                # "pm2.5_10minute_b": 0.0,
                # "pm2.5_30minute": 0.0,
                # "pm2.5_30minute_a": 0.0,
                # "pm2.5_30minute_b": 0.0,
                # "pm2.5_60minute": 0.0,
                # "pm2.5_60minute_a": 0.0,
                # "pm2.5_60minute_b": 0.0,
                # "pm2.5_6hour": 0.0,
                # "pm2.5_6hour_a": 0.0,
                # "pm2.5_6hour_b": 0.0,
                # "pm2.5_24hour": 0.0,
                # "pm2.5_24hour_a": 0.0,
                # "pm2.5_24hour_b": 0.0,
                # "pm2.5_1week": 0.0,
                # "pm2.5_1week_a": 0.0,
                # "pm2.5_1week_b": 0.0,

                ###### PM10.0 fields: ######
                if "p_10_0_um_b" not in sensor_dict.keys():
                    the_modified_sensor_data["pm10.0"] = sensor_dict["p_10_0_um"]
                    the_modified_sensor_data["pm10.0_a"] = sensor_dict["p_10_0_um"]

                else:
                    the_modified_sensor_data["pm10.0"] = float(
                        (sensor_dict["p_10_0_um"] + sensor_dict["p_10_0_um_b"]) / 2
                    )
                    the_modified_sensor_data["pm10.0_a"] = sensor_dict["p_10_0_um"]
                    the_modified_sensor_data["pm10.0_b"] = sensor_dict["p_10_0_um_b"]

                if "pm10_0_atm_b" not in sensor_dict.keys():
                    the_modified_sensor_data["pm10.0_atm"] = sensor_dict["pm10_0_atm"]
                    the_modified_sensor_data["pm10.0_atm_a"] = sensor_dict["pm10_0_atm"]

                else:
                    the_modified_sensor_data["pm10.0_atm"] = float(
                        (sensor_dict["pm10_0_atm"] + sensor_dict["pm10_0_atm_b"]) / 2
                    )
                    the_modified_sensor_data["pm10.0_atm_a"] = sensor_dict["pm10_0_atm"]
                    the_modified_sensor_data["pm10.0_atm_b"] = sensor_dict[
                        "pm10_0_atm_b"
                    ]

                if "pm10_0_cf_1_b" not in sensor_dict.keys():
                    the_modified_sensor_data["pm10.0_cf_1"] = sensor_dict["pm10_0_cf_1"]
                    the_modified_sensor_data["pm10.0_cf_1_a"] = sensor_dict[
                        "pm10_0_cf_1"
                    ]

                else:
                    the_modified_sensor_data["pm10.0_cf_1"] = float(
                        (sensor_dict["pm10_0_cf_1"] + sensor_dict["pm10_0_cf_1_b"]) / 2
                    )
                    the_modified_sensor_data["pm10.0_cf_1_a"] = sensor_dict[
                        "pm10_0_cf_1"
                    ]
                    the_modified_sensor_data["pm10.0_cf_1_b"] = sensor_dict[
                        "pm10_0_cf_1_b"
                    ]

                ###### Particle count fields: #####
                # "0.3_um_count": 0.0,
                # "0.3_um_count_a": 0.0,
                # "0.3_um_count_b": 0.0,
                # "0.5_um_count": 0.0,
                # "0.5_um_count_a": 0.0,
                # "0.5_um_count_b": 0.0,
                # "1.0_um_count": 0.0,
                # "1.0_um_count_a": 0.0,
                # "1.0_um_count_b": 0.0,
                # "2.5_um_count": 0.0,
                # "2.5_um_count_a": 0.0,
                # "2.5_um_count_b": 0.0,
                # "5.0_um_count": 0.0,
                # "5.0_um_count_a": 0.0,
                # "5.0_um_count_b": 0.0,
                # "10.0_um_count": 0.0,
                # "10.0_um_count_a": 0.0,
                # "10.0_um_count_b": 0.0,

                ###### ThingSpeak fields, used to retrieve data from api.thingspeak.com: #####
                # "primary_id_a": 0,
                # "primary_key_a": "",
                # "secondary_id_a": 0,
                # "secondary_key_a": "",
                # "primary_id_b": 0,
                # "primary_key_b": "",
                # "secondary_id_b": 0,
                # "secondary_key_b": "",

                the_modified_sensor_data = self._validate_sensor_data_before_insert(
                    the_modified_sensor_data
                )
                self.store_sensor_data(the_modified_sensor_data)

            debug_log(
                f"""Waiting {json_config_file["poll_interval_seconds"]} seconds before
                    requesting new data again..."""
            )

            del local_sensor_dict
            sleep(json_config_file["poll_interval_seconds"])

    def _construct_store_sensor_data_type(self, raw_data) -> list:
        """
        A method to build the dict data type that the store_sensor_data method expects.

        :param dict raw_data: The return value from either self._purpleair_api_obj.request_members_data or
                              self._purpleair_api_obj.request_multiple_sensors_data.

        :return A list full of the dict data type that the store_sensor_data method expects.
        """

        # Extract the 'fields' and 'data' parts to make it easier on ourselves
        extracted_fields = None
        extracted_data = None
        extracted_fields = raw_data["fields"]
        extracted_data = raw_data["data"]
        store_sensor_data_type_list = []

        # Grab each list of data items from extracted data
        for data_list in extracted_data:
            # Start making our modified sensor data object that will be passed to the
            # self.store_sensor_data() method
            the_modified_sensor_data_dict = {}
            the_modified_sensor_data_dict["data_time_stamp"] = raw_data[
                "data_time_stamp"
            ]
            for data_index, data_item in enumerate(data_list):
                the_modified_sensor_data_dict[
                    str(extracted_fields[data_index])
                ] = data_item

            the_modified_sensor_data_dict = self._validate_sensor_data_before_insert(
                the_modified_sensor_data_dict
            )

            store_sensor_data_type_list.append(the_modified_sensor_data_dict)

        # Delete some stuff
        del extracted_fields
        del extracted_data
        del raw_data

        return store_sensor_data_type_list

    def validate_parameters_and_run(
        self,
        paa_multiple_sensor_request_json_file=None,
        paa_single_sensor_request_json_file=None,
        paa_group_sensor_request_json_file=None,
        paa_local_sensor_request_json_file=None,
    ) -> None:
        """
        A method to choose what run method to execute based on what config file is being used.
        This shall be considered the main entry point for and PurpleAirDataLogger.

        :param str paa_multiple_sensor_request_json_file: The path to a json file containing
                                                          the parameters to send a single sensor request(s).
        :param str paa_single_sensor_request_json_file: The path to a json file containing
                                                        the parameters to send a multiple sensor request(s).
        :param str paa_group_sensor_request_json_file: The path to a json file containing
                                                        the parameters to send a group sensor request(s).
        :param str paa_local_sensor_request_json_file: The path to a json file containing
                                                        the parameters to send a local sensor request(s).
        """

        # Choose what run method to execute depending on
        # paa_multiple_sensor_request_json_file/paa_single_sensor_request_json_file/paa_group_sensor_request_json_file/paa_local_sensor_request_json_file
        if (
            paa_multiple_sensor_request_json_file is not None
            and paa_single_sensor_request_json_file is None
            and paa_group_sensor_request_json_file is None
            and paa_local_sensor_request_json_file is None
        ):
            # Now load up that json file
            file_obj = open(paa_multiple_sensor_request_json_file, "r")
            the_json_file = json.load(file_obj)
            file_obj.close()
            self._run_loop_for_storing_multiple_sensors_data(the_json_file)

        elif (
            paa_multiple_sensor_request_json_file is None
            and paa_single_sensor_request_json_file is not None
            and paa_group_sensor_request_json_file is None
            and paa_local_sensor_request_json_file is None
        ):
            # Now load up that json file
            file_obj = open(paa_single_sensor_request_json_file, "r")
            the_json_file = json.load(file_obj)
            file_obj.close()
            self._run_loop_for_storing_single_sensor_data(the_json_file)

        elif (
            paa_multiple_sensor_request_json_file is None
            and paa_single_sensor_request_json_file is None
            and paa_group_sensor_request_json_file is not None
            and paa_local_sensor_request_json_file is None
        ):
            # Now load up that json file
            file_obj = open(paa_group_sensor_request_json_file, "r")
            the_json_file = json.load(file_obj)
            file_obj.close()
            self._run_loop_for_storing_group_sensors_data(the_json_file)

        elif (
            paa_multiple_sensor_request_json_file is None
            and paa_single_sensor_request_json_file is None
            and paa_group_sensor_request_json_file is None
            and paa_local_sensor_request_json_file is not None
        ):
            # Now load up that json file
            file_obj = open(paa_local_sensor_request_json_file, "r")
            the_json_file = json.load(file_obj)
            file_obj.close()
            self._run_loop_for_storing_local_sensors_data(the_json_file)

        elif (
            paa_multiple_sensor_request_json_file is None
            and paa_single_sensor_request_json_file is None
            and paa_group_sensor_request_json_file is None
            and paa_local_sensor_request_json_file is None
        ):
            raise PurpleAirDataLoggerError(
                """Neither '-paa_multiple_sensor_request_json_file' or '-paa_single_sensor_request_json_file' or '-paa_group_sensor_request_json_file' or 'and paa_local_sensor_request_json_file is' were provided. Please provide at least one!"""
            )

        else:
            raise PurpleAirDataLoggerError(
                """One parameter '-paa_multiple_sensor_request_json_file' or '-paa_single_sensor_request_json_file' or '-paa_group_sensor_request_json_file'  or 'and paa_local_sensor_request_json_file is must be provided. Not all!"""
            )
