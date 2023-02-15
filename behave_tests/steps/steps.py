#!/usr/bin/env python3

"""
    Copyright 2022 carlkid1499, All rights reserved.
    Steps for behavior driven tests for the purpleair_data_logger.
"""

from behave import given, when, then
from json import load, dumps
import subprocess
from hamcrest import assert_that, equal_to, is_, is_in
from time import sleep

SLEEP_BETWEEN_REPEATED_API_CALLS = 1.1 * 60  # mins * seconds


@given(
    "we do not provide {settings_field} in {config_file_type} sensor configuration file"
)
def create_configuration_file_with_settings_field_omitted(
    context, config_file_type=None, settings_field=None
):
    if settings_field is None:
        raise ValueError(
            "In step 'create_configuration_file_with_settings_field_omitted' parameter 'settings_field' can not be `None`!"
        )

    if config_file_type is None:
        raise ValueError(
            "In step 'create_configuration_file_with_settings_field_omitted' parameter 'config_file_type' can not be `None`!"
        )

    # Open up ../sample_json_config_files/sample_multiple_sensor_request_json_file.json
    read_file_obj = open(
        f"../sample_json_config_files/sample_{config_file_type}_sensor_request_json_file.json",
        "r",
    )

    # Read in the json file into a python3 dict
    json_file_contents = load(read_file_obj)
    read_file_obj.close()

    # Remove settings_field from json file contents
    del json_file_contents[str(settings_field)]

    # Write new file to disk
    context.test_settings_file_name = (
        f"{config_file_type}_settings_file_with_{settings_field}_removed.json"
    )
    context.settings_field_being_removed = settings_field
    context.test_settings_file_name_and_path = (
        context.logs_path + f"/{context.test_settings_file_name}"
    )
    json_file_contents = dumps(json_file_contents)
    write_file_obj = open(context.test_settings_file_name_and_path, "x")
    write_file_obj.write(json_file_contents)
    write_file_obj.flush()
    write_file_obj.close()


@when(
    "we start the CSVDatalogger using above {config_file_type} sensor configuration file"
)
def start_the_csv_data_logger(context, config_file_type=None):
    if config_file_type is None:
        raise ValueError(
            "In step 'start_the_csv_data_logger' parameter 'config_file_type' can not be `None`!"
        )

    # Launch the CSVDataLogger with test_settings_file_name_and_path
    context.csvdatalogger_save_file_path = (
        context.logs_path + "/" + "csvdatalogger_outputs"
    )

    if config_file_type == "single":
        command_args = [
            "python3",
            "-m",
            "purpleair_data_logger.PurpleAirCSVDataLogger",
            "-save_file_path",
            f"{context.csvdatalogger_save_file_path}",
            "-paa_read_key",
            f"{context.config.userdata['PAA_API_READ_KEY']}",
            "-paa_single_sensor_request_json_file",
            f"{context.test_settings_file_name_and_path}",
        ]

    elif config_file_type == "multiple":
        command_args = [
            "python3",
            "-m",
            "purpleair_data_logger.PurpleAirCSVDataLogger",
            "-save_file_path",
            f"{context.csvdatalogger_save_file_path}",
            "-paa_read_key",
            f"{context.config.userdata['PAA_API_READ_KEY']}",
            "-paa_multiple_sensor_request_json_file",
            f"{context.test_settings_file_name_and_path}",
        ]

    else:
        raise ValueError(
            "Invalid option for 'start_the_csv_data_logger' parameter 'config_file_type'!"
        )

    # Create stdout and stderr files
    context.stdout_file_obj = open(
        f"{context.test_settings_file_name_and_path}.stdout", "x"
    )
    context.stderr_file_obj = open(
        f"{context.test_settings_file_name_and_path}.stderr", "x"
    )

    context.subproc_for_datalogger = subprocess.Popen(
        args=command_args,
        stdout=context.stdout_file_obj,
        stderr=context.stderr_file_obj,
    )

    sleep(SLEEP_BETWEEN_REPEATED_API_CALLS)


@then("the CSVDatalogger should {expected_outcome} with error message {error_message}")
def check_started_data_logger(context, expected_outcome=None, error_message=None):
    if expected_outcome is None:
        raise ValueError(
            "In step 'check_started_data_logger' parameter 'expected_outcome' can not be `None`!"
        )

    if error_message is None:
        raise ValueError(
            "In step 'check_started_data_logger' parameter 'error_message' can not be `None`!"
        )

    # Now kill the proc, we are done with it
    context.stdout_file_obj.flush()
    context.stderr_file_obj.flush()
    context.subproc_for_datalogger.kill()
    context.stdout_file_obj.close()
    context.stderr_file_obj.close()

    file_err_obj = open(f"{context.test_settings_file_name_and_path}.stderr", "r")
    file_err_contents = file_err_obj.read()
    file_err_obj.close()

    file_out_obj = open(f"{context.test_settings_file_name_and_path}.stdout", "r")
    file_out_contents = file_out_obj.read()
    file_out_obj.close()

    file_out_contents = str(file_out_contents)
    file_err_contents = str(file_err_contents)
    multi_run_loop_msg = (
        "_run_loop_for_storing_multiple_sensors_data - Beep boop I am alive..."
    )
    single_run_loop_msg = (
        "_run_loop_for_storing_single_sensor_data - Beep boop I am alive..."
    )

    if expected_outcome == "not start":
        if "single" in context.test_settings_file_name_and_path:
            assert_that(
                single_run_loop_msg,
                is_in(file_out_contents),
                "Checking contents of stdout file...",
            )

        elif "multiple" in context.test_settings_file_name_and_path:
            assert_that(
                multi_run_loop_msg,
                is_in(file_out_contents),
                "Checking contents of stdout file...",
            )
        else:
            raise ValueError("Invalid file. Only `single` or `multiple` supported!")

        if error_message != "None":
            assert_that(
                error_message,
                is_in(file_err_contents),
                "Checking contents of stderr file...",
            )

        assert_that(
            context.subproc_for_datalogger.returncode,
            equal_to(1),
            "Checking subproc return code...",
        )

    elif expected_outcome == "start":
        # This if statement here is to please tests when ran under python 3.9/10 on windows.
        if (
            context.python_version_list[0] == "3"
            and (
                context.python_version_list[1] == "9"
                or context.python_version_list[1] == "10"
            )
            and context.operating_system == "windows"
            and (
                [
                    "multiple_settings_file_with_custom_fields_value_2",
                    "multiple_settings_file_with_custom_location_type_value_2",
                    "multiple_settings_file_with_custom_max_age_value_1",
                    "multiple_settings_file_with_custom_modified_since_value_1",
                ]
                in context.test_settings_file_name_and_path
            )
        ):
            assert_that(
                multi_run_loop_msg,
                is_in(file_out_contents),
                "Checking contents of stdout file...",
            )

            assert_that(
                "We weren't able to write the current data!",
                is_in(file_out_contents),
                "Checking contents of stdout file...",
            )

            assert_that(
                file_err_contents, is_(""), "Checking contents of stderr file..."
            )

        else:
            assert_that(
                file_out_contents, is_(""), "Checking contents of stdout file..."
            )
            assert_that(
                file_err_contents, is_(""), "Checking contents of stderr file..."
            )

        assert_that(
            context.subproc_for_datalogger.returncode,
            equal_to(None),
            "Checking subproc return code...",
        )

    else:
        raise ValueError(f"{expected_outcome} is not a valid case!")


@given("we set {field} in {config_file_type} sensor configuration file to {value}")
def set_field_in_json_to_value(context, field=None, config_file_type=None, value=None):
    if field is None:
        raise ValueError(
            "In step 'set_field_in_json_to_value' parameter 'field' can not be `None`!"
        )

    if config_file_type is None:
        raise ValueError(
            "In step 'set_field_in_json_to_value' parameter 'config_file_type' can not be `None`!"
        )

    if value is None:
        raise ValueError(
            "In step 'set_field_in_json_to_value' parameter 'value' can not be `None`!"
        )

    # Open up ../sample_json_config_files/sample_multiple_sensor_request_json_file.json
    read_file_obj = open(
        f"../sample_json_config_files/sample_{config_file_type}_sensor_request_json_file.json",
        "r",
    )

    # Read in the json file into a python3 dict
    json_file_contents = load(read_file_obj)
    read_file_obj.close()

    json_file_contents[str(field)] = value

    # Write new file to disk
    did_we_write_a_new_file = False
    file_creation_counter = 1

    while did_we_write_a_new_file == False:
        try:
            context.test_settings_file_name = f"{config_file_type}_settings_file_with_custom_{field}_value_{file_creation_counter}.json"
            context.test_settings_file_name_and_path = (
                context.logs_path + f"/{context.test_settings_file_name}"
            )
            json_file_contents_out = None
            json_file_contents_out = dumps(json_file_contents)
            write_file_obj = open(context.test_settings_file_name_and_path, "x")
            write_file_obj.write(json_file_contents_out)
            write_file_obj.flush()
            write_file_obj.close()
            did_we_write_a_new_file = True

        except FileExistsError:
            file_creation_counter = file_creation_counter + 1
