#!/usr/bin/env python3

"""
    Copyright 2022 carlkid1499, All rights reserved.
    Steps for behavior driven tests for the purpleair_data_logger.
"""

from behave import given, when, then
from json import load, dumps
import subprocess
from hamcrest import assert_that, equal_to, is_
from time import sleep

SLEEP_BETWEEN_REPEATED_API_CALLS = 65  # seconds


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
    del json_file_contents[str(settings_field)]

    # Write new file to disk
    context.test_settings_file_name = f"settings_file_with_{settings_field}_removed.json"
    context.settings_field_being_removed = settings_field
    context.test_settings_file_name_and_path = context.logs_path + \
        f"/{context.test_settings_file_name}"
    json_file_contents = dumps(json_file_contents)
    write_file_obj = open(context.test_settings_file_name_and_path, "x")
    write_file_obj.write(json_file_contents)
    write_file_obj.flush()
    write_file_obj.close()


@when("we start the CSVDatalogger using above configuration file")
def start_the_csv_data_logger(context):

    # Launch the CSVDataLogger with test_settings_file_name_and_path
    command_args = ["python3", "-m", "purpleair_data_logger.PurpleAirCSVDataLogger",
                    "-save_file_path", f"{context.logs_path}",
                    "-paa_read_key", f"{context.config.userdata['PAA_API_READ_KEY']}",
                    "-paa_multiple_sensor_request_json_file", f"{context.test_settings_file_name_and_path}"]

    # Create stdout and stderr files
    stdout_file_obj = open(
        f"{context.test_settings_file_name_and_path}.stdout", "x")
    stderr_file_obj = open(
        f"{context.test_settings_file_name_and_path}.stderr", "x")

    context.subproc_for_datalogger = subprocess.run(
        args=command_args, stdout=stdout_file_obj, stderr=stderr_file_obj)

    stdout_file_obj.flush()
    stdout_file_obj.close()
    stderr_file_obj.flush()
    stderr_file_obj.close()

    sleep(SLEEP_BETWEEN_REPEATED_API_CALLS)


@then("the CSVDatalogger should {expected_outcome} with error message {error_message}")
def check_started_data_logger(context, expected_outcome=None, error_message=None):

    if expected_outcome is None:
        raise ValueError(
            "In step 'check_started_data_logger' parameter 'expected_outcome' can not be `None`!")

    if error_message is None:
        raise ValueError(
            "In step 'check_started_data_logger' parameter 'error_message' can not be `None`!")

    if expected_outcome == "not start":
        file_err_obj = open(
            f"{context.test_settings_file_name_and_path}.stderr", "r")
        file_err_contents = file_err_obj.read()
        file_err_obj.close()

        file_out_obj = open(
            f"{context.test_settings_file_name_and_path}.stdout", "r")
        file_out_contents = file_out_obj.read()
        file_out_obj.close()

        assert_that(bool(
            "_run_loop_for_storing_multiple_sensors_data - Beep boop I am alive..." in file_out_contents), is_(True), "Checking contents of stdout file...")
        if error_message != "None":
            assert_that(bool(
                f"{error_message}" in file_err_contents), is_(True), "Checking contents of stderr file...")
        assert_that(context.subproc_for_datalogger.returncode, equal_to(1))

    elif expected_outcome == "start":
        file_err_obj = open(
            f"{context.test_settings_file_name_and_path}.stderr", "r")
        file_err_contents = file_err_obj.read()
        file_err_obj.close()

        file_out_obj = open(
            f"{context.test_settings_file_name_and_path}.stdout", "r")
        file_out_contents = file_out_obj.read()
        file_out_obj.close()

        assert_that(bool(
            "_run_loop_for_storing_multiple_sensors_data - Beep boop I am alive..." in file_out_contents), is_(True), "Checking contents of stdout file...")
        if error_message != "None":
            assert_that(bool(
                f"{error_message}" in file_err_contents), is_(True), "Checking contents of stderr file...")

        assert_that(context.subproc_for_datalogger.returncode, equal_to(0))

    else:
        raise ValueError(f"{expected_outcome} is not a valid case!")


@given("we set {field} in configuration file to {value}")
def set_field_in_json_to_value(context, field=None, value=None):

    if field is None:
        raise ValueError(
            "In step 'set_field_in_json_to_value' parameter 'field' can not be `None`!")

    if value is None:
        raise ValueError(
            "In step 'set_field_in_json_to_value' parameter 'value' can not be `None`!")

    # Open up ../sample_json_config_files/sample_multiple_sensor_request_json_file.json
    read_file_obj = open(
        "../sample_json_config_files/sample_multiple_sensor_request_json_file.json", "r")

    # Read in the json file into a python3 dict
    json_file_contents = load(read_file_obj)
    read_file_obj.close()

    json_file_contents[str(field)] = value

    # Write new file to disk
    did_we_write_a_new_file = False
    file_creation_counter = 1

    while did_we_write_a_new_file == False:
        try:
            context.test_settings_file_name = f"settings_file_with_custom_{field}_value_{file_creation_counter}.json"
            context.test_settings_file_name_and_path = context.logs_path + \
                f"/{context.test_settings_file_name}"
            json_file_contents_out = None
            json_file_contents_out = dumps(json_file_contents)
            write_file_obj = open(context.test_settings_file_name_and_path, "x")
            write_file_obj.write(json_file_contents_out)
            write_file_obj.flush()
            write_file_obj.close()
            did_we_write_a_new_file = True
        
        except FileExistsError:
            file_creation_counter = file_creation_counter + 1

