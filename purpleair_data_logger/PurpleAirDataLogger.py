#!/usr/bin/env python3

"""
    Copyright 2023 carlkid1499, All rights reserved.
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
        required=True,
        dest="paa_read_key",
        type=str,
        help="""The PurpleAirAPI Read key""",
    )

    parser.add_argument(
        "-paa_write_key",
        required=True,
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

    def __init__(self, PurpleAirAPIReadKey, PurpleAirAPIWriteKey):
        """
        :param str PurpleAirAPIReadKey: A valid PurpleAirAPI Read key
        :param object psql_db_conn: A valid PG8000 database connection
        """

        # Make one instance of our PurpleAirAPI class
        self._purpleair_api_obj = PurpleAirAPI(
            your_api_read_key=PurpleAirAPIReadKey,
            your_api_write_key=PurpleAirAPIWriteKey,
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

    def _validate_sensor_data_before_insert(self, the_modified_sensor_data):
        """
        Before we store the data, we must make sure all fields have been included
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

        # Then return the modified copy
        return temp_the_modified_sensor_data

    def _run_loop_for_storing_single_sensor_data(self, the_json_file):
        """
        A method containing the run loop for inserting a single sensors' data into the data logger.

        :param dict json_config_file: A dictionary object of the json config file using json load.
        """

        while True:
            print(
                "_run_loop_for_storing_single_sensor_data - Beep boop I am alive...\n\n"
            )
            # We will request data once every 65 seconds.
            debug_log(
                f"""Requesting new data from a sensor with index
                      {the_json_file['sensor_index']}..."""
            )

            sensor_data = self._purpleair_api_obj.request_sensor_data(
                the_json_file["sensor_index"],
                the_json_file["read_key"],
                the_json_file["fields"],
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
                f"""Waiting {self._send_request_every_x_seconds} seconds before
                  requesting new data again..."""
            )
            sleep(self.send_request_every_x_seconds)

    def _run_loop_for_storing_multiple_sensors_data(self, json_config_file):
        """
        A method containing the run loop for inserting a multiple sensors' data into the data logger.

        :param dict json_config_file: A dictionary object of the json config file using json load.
        """

        while True:
            print(
                "_run_loop_for_storing_multiple_sensors_data - Beep boop I am alive...\n\n"
            )
            # We will request data once every 65 seconds.
            debug_log(
                f"""Requesting new data from multiple sensors with fields
                      {json_config_file["fields"]}..."""
            )

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

            store_sensor_data_type_list = self._construct_store_sensor_data_type(
                sensors_data
            )

            for store_sensor_data_type in store_sensor_data_type_list:
                # Store the current data
                self.store_sensor_data(store_sensor_data_type)

            debug_log(
                f"""Waiting {self._send_request_every_x_seconds} seconds before
                  requesting new data again..."""
            )
            sleep(self.send_request_every_x_seconds)

    def _run_loop_for_storing_group_sensors_data(self, json_config_file):
        """
        A method containing the run loop for inserting a group sensors' data into the data logger.

        :param dict json_config_file: A dictionary object of the json config file using json load.
        """

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
                f"""Waiting {self._send_request_every_x_seconds} seconds before
                  requesting new data again..."""
            )

            sleep(self.send_request_every_x_seconds)

    def _construct_store_sensor_data_type(self, raw_data):
        """
        A method to build the dict data type that the store_sensor_data method expects.

        :param dict raw_data: The return value from either self._purpleair_api_obj.request_members_data or
                              self._purpleair_api_obj.request_multiple_sensors_data.
        """

        # Extract the 'fields' and 'data' parts to make it easier on ourselves
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

        return store_sensor_data_type_list

    def validate_parameters_and_run(
        self,
        paa_multiple_sensor_request_json_file=None,
        paa_single_sensor_request_json_file=None,
        paa_group_sensor_request_json_file=None,
    ):
        """
        A method to choose what run method to execute based on what config file is being used.
        This shall be considered the main entry point for and PurpleAirDataLogger.

        :param str paa_multiple_sensor_request_json_file: The path to a json file containing
                                                          the parameters to send a single sensor request(s).
        :param str paa_single_sensor_request_json_file: The path to a json file containing
                                                        the parameters to send a multiple sensor request(s).
        :param str paa_group_sensor_request_json_file: The path to a json file containing
                                                        the parameters to send a group sensor request(s).
        """

        # Choose what run method to execute depending on
        # paa_multiple_sensor_request_json_file/paa_single_sensor_request_json_file/paa_group_sensor_request_json_file
        if (
            paa_multiple_sensor_request_json_file is not None
            and paa_single_sensor_request_json_file is None
            and paa_group_sensor_request_json_file is None
        ):
            # Now load up that json file
            file_obj = open(paa_multiple_sensor_request_json_file, "r")
            the_json_file = json.load(file_obj)
            self._run_loop_for_storing_multiple_sensors_data(the_json_file)

        elif (
            paa_multiple_sensor_request_json_file is None
            and paa_single_sensor_request_json_file is not None
            and paa_group_sensor_request_json_file is None
        ):
            # Now load up that json file
            file_obj = open(paa_single_sensor_request_json_file, "r")
            the_json_file = json.load(file_obj)
            self._run_loop_for_storing_single_sensor_data(the_json_file)

        elif (
            paa_multiple_sensor_request_json_file is None
            and paa_single_sensor_request_json_file is None
            and paa_group_sensor_request_json_file is not None
        ):
            # Now load up that json file
            file_obj = open(paa_group_sensor_request_json_file, "r")
            the_json_file = json.load(file_obj)
            self._run_loop_for_storing_group_sensors_data(the_json_file)

        elif (
            paa_multiple_sensor_request_json_file is None
            and paa_single_sensor_request_json_file is None
            and paa_group_sensor_request_json_file is None
        ):
            raise PurpleAirDataLoggerError(
                """Neither '-paa_multiple_sensor_request_json_file' or '-paa_single_sensor_request_json_file' or '-paa_group_sensor_request_json_file' were provided. Please provide at least one!"""
            )

        else:
            raise PurpleAirDataLoggerError(
                """One parameter '-paa_multiple_sensor_request_json_file' or '-paa_single_sensor_request_json_file' or '-paa_group_sensor_request_json_file' must be provided. Not all!"""
            )
