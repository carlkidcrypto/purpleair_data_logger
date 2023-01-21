#!/usr/bin/env python3

"""
    Copyright 2022 carlkid1499, All rights reserved.
    A python base Data Logger class.
"""

from purpleair_data_logger.PurpleAirAPI import PurpleAirAPI, debug_log
from purpleair_data_logger.PurpleAirAPIConstants import ACCEPTED_FIELD_NAMES_DICT
from time import sleep
import json


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
    example, PSQLDataLogger and CSVDataLogger. Inheritors of this class will only need to define
    their own 'store_sensor_data' method.
    """

    def __init__(self, PurpleAirAPIReadKey):
        """
        :param str PurpleAirAPIReadKey: A valid PurpleAirAPI Read key
        :param object psql_db_conn: A valid PG8000 database connection
        """

        # Make one instance of our PurpleAirAPI class
        self._purple_air_api_obj = PurpleAirAPI(your_api_read_key=PurpleAirAPIReadKey)

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
        A method containing the run loop for inserting a single sensors' data into the db.

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

            sensor_data = self._purple_air_api_obj.request_sensor_data(
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
            sleep(self._send_request_every_x_seconds)

    def _run_loop_for_storing_multiple_sensors_data(self, json_config_file):
        """
        A method containing the run loop for inserting a multiple sensors' data into the db.

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

            sensors_data = self._purple_air_api_obj.request_multiple_sensors_data(
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

            # Extract the 'fields' and 'data' parts to make it easier on ourselves
            extracted_fields = sensors_data["fields"]
            extracted_data = sensors_data["data"]

            # Grab each list of data items from extracted data
            for data_list in extracted_data:
                # Start making our modified sensor data object that will be passed to the
                # self.store_sensor_data() method
                the_modified_sensor_data = {}
                the_modified_sensor_data["data_time_stamp"] = sensors_data[
                    "data_time_stamp"
                ]
                for data_index, data_item in enumerate(data_list):
                    the_modified_sensor_data[
                        str(extracted_fields[data_index])
                    ] = data_item

                the_modified_sensor_data = self._validate_sensor_data_before_insert(
                    the_modified_sensor_data
                )

                # Store the current data
                self.store_sensor_data(the_modified_sensor_data)

            debug_log(
                f"""Waiting {self._send_request_every_x_seconds} seconds before
                  requesting new data again..."""
            )
            sleep(self._send_request_every_x_seconds)

    def validate_parameters_and_run(
        self,
        paa_multiple_sensor_request_json_file=None,
        paa_single_sensor_request_json_file=None,
    ):
        """
        A method to choose what run method to execute based on what config file is being used.
        This shall be considered the main entry point for and PurpleAirDataLogger.

        :param str paa_multiple_sensor_request_json_file: The path to a json file containing
                                                          the parameters to send a single sensor request.
        :param str paa_single_sensor_request_json_file: The path to a json file containing
                                                        the parameters to send a multiple sensor request.
        """

        # Third choose what run method to execute depending on paa_multiple_sensor_request_json_file/paa_single_sensor_request_json_file
        if (
            paa_multiple_sensor_request_json_file is not None
            and paa_single_sensor_request_json_file is None
        ):
            # Now load up that json file
            file_obj = open(paa_multiple_sensor_request_json_file, "r")
            the_json_file = json.load(file_obj)
            self._run_loop_for_storing_multiple_sensors_data(the_json_file)

        elif (
            paa_multiple_sensor_request_json_file is None
            and paa_single_sensor_request_json_file is not None
        ):
            # Now load up that json file
            file_obj = open(paa_single_sensor_request_json_file, "r")
            the_json_file = json.load(file_obj)
            self._run_loop_for_storing_single_sensor_data(the_json_file)

        elif (
            paa_multiple_sensor_request_json_file is None
            and paa_single_sensor_request_json_file is None
        ):
            raise PurpleAirDataLoggerError(
                """Neither '-paa_multiple_sensor_request_json_file' or '-paa_single_sensor_request_json_file' were provided. Please provide at least one!"""
            )

        else:
            raise PurpleAirDataLoggerError(
                """One parameter '-paa_multiple_sensor_request_json_file' or '-paa_single_sensor_request_json_file' must be provided. Not both!"""
            )
