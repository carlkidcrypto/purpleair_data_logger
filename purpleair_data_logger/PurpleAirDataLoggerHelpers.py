#!/usr/bin/env python3

"""
    Copyright 2023 carlkidcrypto, All rights reserved.
    A helper file that contains constants and functions for PurpleAirDataLogger* files.
"""

from purpleair_api.PurpleAirAPIConstants import ACCEPTED_FIELD_NAMES_DICT
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


def validate_sensor_data_before_insert(the_modified_sensor_data) -> dict:
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
            temp_the_modified_sensor_data[str(field)] = ACCEPTED_FIELD_NAMES_DICT[field]

    # Delete some stuff
    del the_modified_sensor_data

    # Then return the modified copy
    return temp_the_modified_sensor_data


def construct_store_sensor_data_type(raw_data) -> list:
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
        the_modified_sensor_data_dict["data_time_stamp"] = raw_data["data_time_stamp"]
        for data_index, data_item in enumerate(data_list):
            the_modified_sensor_data_dict[str(extracted_fields[data_index])] = data_item

        the_modified_sensor_data_dict = validate_sensor_data_before_insert(
            the_modified_sensor_data_dict
        )

        store_sensor_data_type_list.append(the_modified_sensor_data_dict)

    # Delete some stuff
    del extracted_fields
    del extracted_data
    del raw_data

    return store_sensor_data_type_list
