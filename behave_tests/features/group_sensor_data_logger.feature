###############################################################################
# Copyright 2023 carlkidcrypto, All rights reserved.
# Behavior driven tests for the purpleair_data_logger.
# This file will test the Behavior for the CSVDatalogger when a
# group sensor configuration file is passed in
###############################################################################

Feature: A group sensor configuration file is passed into the CSVDatalogger

    Scenario Outline: An invalid group sensor configuration file is provided
        Given we do not provide <settings_field> in group sensor configuration file
        When we start the CSVDatalogger using above group sensor configuration file
        Then the CSVDatalogger should not start with error message KeyError: '<settings_field>'
        @group_sensors_omit
        Examples: group sensor configuration setting to omit
            | settings_field       |
            | sensor_group_name    |
            | add_sensors_to_group |
            | sensor_index_list    |
            | fields               |
            | location_type        |
            | read_keys            |
            | show_only            |
            | modified_since       |
            | max_age              |
            | nwlng                |
            | nwlat                |
            | selng                |
            | selat                |

    Scenario Outline: Provide valid and invalid values to the json fields inside the group sensor configuration settings file
        Given we set <field> in group sensor configuration file to <value>
        When we start the CSVDatalogger using above group sensor configuration file
        Then the CSVDatalogger should <expected_result> with error message <error_message>
        @group_sensors_valid_invalid
        Examples: Pass valid and invalid values to the fields inside configuration settings file
            | field          | value                                                                                                      | expected_result | error_message                                                                                                                                      |
            | fields         | null                                                                                                       | not start       | purpleair_api.PurpleAirAPI.PurpleAirAPIError: 400: InvalidFieldValueError - A provided field (null) was not found.                                 |
            | fields         | name                                                                                                       | start           | None                                                                                                                                               |
            | fields         | position_rating, firmware_version, firmware_upgrade, channel_state, channel_flags, channel_flags_manual    | start           | None                                                                                                                                               |
            | location_type  | -1                                                                                                         | not start       | purpleair_api.PurpleAirAPI.PurpleAirAPIError: 400: InvalidLocationTypeError - Invalid location type. Permitted values are 0 = outside, 1 = inside. |
            | location_type  | 0                                                                                                          | start           | None                                                                                                                                               |
            | location_type  | 1                                                                                                          | start           | None                                                                                                                                               |
            | location_type  | 2                                                                                                          | not start       | purpleair_api.PurpleAirAPI.PurpleAirAPIError: 400: InvalidLocationTypeError - Invalid location type. Permitted values are 0 = outside, 1 = inside. |
            | show_only      | 83821, 158705, 83611                                                                                       | start           | None                                                                                                                                               |
            | modified_since | 1671334756                                                                                                 | start           | None                                                                                                                                               |
            | max_age        | 300                                                                                                        | start           | None                                                                                                                                               |
