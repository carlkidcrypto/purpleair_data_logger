#!/usr/bin/env python3

"""
    Copyright 2023 carlkidcrypto, All rights reserved.
    A python base Data Logger class.
"""

from purpleair_api.PurpleAirAPI import PurpleAirAPI
from purpleair_data_logger.PurpleAirDataLoggerHelpers import (
    logic_for_storing_single_sensor_data,
    logic_for_storing_multiple_sensors_data,
    logic_for_storing_group_sensors_data,
    logic_for_storing_local_sensors_data,
)
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

    def _run_loop_for_storing_single_sensor_data(self, json_config_file) -> None:
        """
        A method containing the run loop for inserting a single sensors' data into the data logger.

        :param dict json_config_file: A dictionary object of the json config file using json load.
        :return: None
        """

        # Set the polling interval
        self.send_request_every_x_seconds = json_config_file["poll_interval_seconds"]

        while True:
            print(
                "_run_loop_for_storing_single_sensor_data - Beep boop I am alive...\n\n"
            )
            logic_for_storing_single_sensor_data(self, json_config_file)
            sleep(self.send_request_every_x_seconds)

    def _run_loop_for_storing_multiple_sensors_data(self, json_config_file) -> None:
        """
        A method containing the run loop for inserting a multiple sensors' data into the data logger.

        :param dict json_config_file: A dictionary object of the json config file using json load.
        :return: None
        """

        # Set the polling interval
        self.send_request_every_x_seconds = json_config_file["poll_interval_seconds"]

        while True:
            print(
                "_run_loop_for_storing_multiple_sensors_data - Beep boop I am alive...\n\n"
            )
            logic_for_storing_multiple_sensors_data(self, json_config_file)
            sleep(self.send_request_every_x_seconds)

    def _run_loop_for_storing_group_sensors_data(self, json_config_file) -> None:
        """
        A method containing the run loop for inserting a group sensors' data into the data logger.

        :param dict json_config_file: A dictionary object of the json config file using json load.
        :return: None
        """

        # Set the polling interval
        self.send_request_every_x_seconds = json_config_file["poll_interval_seconds"]

        group_id_to_use = None
        while True:
            print(
                "_run_loop_for_storing_group_sensors_data - Beep boop I am alive...\n\n"
            )
            group_id_to_use = logic_for_storing_group_sensors_data(
                self, group_id_to_use, json_config_file
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
            logic_for_storing_local_sensors_data(self, json_config_file)
            sleep(json_config_file["poll_interval_seconds"])

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
