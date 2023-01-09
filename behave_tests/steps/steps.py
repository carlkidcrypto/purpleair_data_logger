#!/usr/bin/env python3

"""
    Copyright 2022 carlkid1499, All rights reserved.
    Steps for behavior driven tests for the purpleair_data_logger.
"""

from behave import given
from json import load, dumps
import subprocess
from hamcrest import assert_that, equal_to, is_not


@given("we do not provide {settings_field} in configuration file")
def create_configuration_file_with_settings_field_omitted(context, settings_field=None):

    if settings_field is None:
        raise ValueError(
            "In step 'create_configuration_file_with_settings_field_omitted' parameter 'settings_field' can not be `None`!")

    # Open up ../sample_json_config_files/sample_multiple_sensor_request_json_file.json
    read_file_obj = open(
        "../sample_json_config_files/sample_multiple_sensor_request_json_file.json", "r")

    # Read in the json file into a python3 dict
    json_file_contents = load(read_file_obj)
    read_file_obj.close()

    # Remove settings_field from json file contents
    del json_file_contents["fields"]

    # Write new file to disk and launch the CSVDataLogger
    test_settings_file_name_and_path = context.logs_path + \
        f"/settings_file_with_{settings_field}_removed.json"
    json_file_contents = dumps(json_file_contents)
    write_file_obj = open(test_settings_file_name_and_path, "x")
    write_file_obj.write(json_file_contents)
    write_file_obj.flush()
    write_file_obj.close()

    # Launch the CSVDataLogger with test_settings_file_name_and_path
    DELETE_ME_DO_NOT_PUSH_TO_GITHUB = ""
    command_args = ["python3", "-m", "purpleair_data_logger.PurpleAirCSVDataLogger", "-save_file_path",
                    f"{context.logs_path}", "-paa_read_key", f"{DELETE_ME_DO_NOT_PUSH_TO_GITHUB}", "-paa_multiple_sensor_request_json_file", f"{test_settings_file_name_and_path}"]
    
    proc = subprocess.run(args=command_args)
    assert_that(proc.returncode, equal_to(1))
