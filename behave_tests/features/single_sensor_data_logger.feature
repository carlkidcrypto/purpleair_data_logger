###############################################################################
# Copyright 2022 carlkidcrypto, All rights reserved.
# Behavior driven tests for the purpleair_data_logger.
# This file will test the Behavior for the CSVDatalogger when a
# single sensor configuration file is passed in
###############################################################################

Feature: A single sensor configuration file is passed into the CSVDatalogger

    Scenario Outline: An invalid single sensor configuration file is provided
        Given we do not provide <settings_field> in single sensor configuration file
        When we start the CSVDatalogger using above single sensor configuration file
        Then the CSVDatalogger should not start with error message KeyError: '<settings_field>'
        @single_sensor_omit
        Examples: Single sensor configuration setting to omit
            | settings_field |
            | sensor_index   |
            | read_key       |
            | fields         |

    Scenario Outline: Provide valid and invalid values to the json fields inside the single sensor configuration settings file
    Given we set <field> in single sensor configuration file to <value>
    When we start the CSVDatalogger using above single sensor configuration file
    Then the CSVDatalogger should <expected_result> with error message <error_message>
    @single_sensor_valid_invalid
    Examples: Pass valid and invalid values to the fields inside configuration settings file
        | field          | value                                                                                                      | expected_result | error_message                                                                                                                                  |
        | sensor_index   | -1                                                                                                         | not start       | purpleair_api.PurpleAirAPI.PurpleAirAPIError: 400: InvalidParameterValueError - The value provided for parameter 'sensor_index' was not valid. |
        | sensor_index   | 160387                                                                                                     | start           | None                                                                                                                                           |
        | fields         | names                                                                                                      | not start       | purpleair_api.PurpleAirAPI.PurpleAirAPIError: 400: InvalidFieldValueError - A provided field (names) was not found.                            |
        | fields         | name                                                                                                       | start           | None                                                                                                                                           |
        | fields         | position_rating, firmware_version, firmware_upgrade, channel_state, channel_flags, channel_flags_manual    | start           | None                                                                                                                                           |