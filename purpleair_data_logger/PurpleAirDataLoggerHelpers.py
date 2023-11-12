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


def flatten_single_sensor_data(raw_data) -> dict:
    """
    A method to flatten the raw data from a single sensor request. This makes our logic downstream easier.

    :param dict raw_data: The return value from self._purpleair_api_obj.request_sensor_data.

    :return A single level dict full request_sensor_data data.
    """

    # Let's make it easier on ourselves by making the sensor data one level deep.
    # Instead of json["sensor"]["KEYS..."] and json["sensor"]["stats_a"]["KEYS..."] etc
    # We turn it into just json["KEYS..."].
    the_modified_sensor_data = {}
    the_modified_sensor_data["data_time_stamp"] = raw_data["data_time_stamp"]
    for key, val in raw_data["sensor"].items():
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
            the_modified_sensor_data[f"pm2.5_6hour_{key[-1]}"] = val["pm2.5_6hour"]
            the_modified_sensor_data[f"pm2.5_24hour_{key[-1]}"] = val["pm2.5_24hour"]
            the_modified_sensor_data[f"pm2.5_1week_{key[-1]}"] = val["pm2.5_1week"]
            the_modified_sensor_data[f"time_stamp_{key[-1]}"] = val["time_stamp"]

        else:
            the_modified_sensor_data[key] = val

    return the_modified_sensor_data
