###############################################################################
# Copyright 2022 carlkid1499, All rights reserved.
# Behavior driven tests for the purpleair_data_logger.
# This file will test the Behavior for the CSVDatalogger when a
# multiple sensor configuration file is passed in
###############################################################################

Feature: A multiple sensor configuration file is passed into the CSVDatalogger

    Scenario Outline: An invalid configuration file is provided
        Given we do not provide <settings_field> in configuration file
        When we start the CSVDatalogger using above configuration file
        Then the CSVDatalogger should not start with error message KeyError: '<settings_field>'

        Examples: Configuration setting to omit
            | settings_field |
            | fields         |
            | location_type  |
            | read_keys      |
            | show_only      |
            | modified_since |
            | max_age        |
            | nwlng          |
            | nwlat          |
            | selng          |
            | selat          |

    @wip
    Scenario Outline: Provide valid and invalid values to the 'fields' json field inside the configuration settings file
        Given we set <field> in configuration file to <value>
        When we start the CSVDatalogger using above configuration file
        Then the CSVDatalogger should <expected_result> with error message <error_message>
    
        Examples: Pass valid and invalid values to the 'fields' field inside configuration settings file
            | field          | value                                                                                                      | expected_result | error_message                                                                                                              |
            | fields         | null                                                                                                       | not start       | purpleair_data_logger.PurpleAirAPI.PurpleAirAPIError: 400: InvalidFieldValueError - A provided field (null) was not found. |
            | fields         | name                                                                                                       | start           | None                                                                                                                       |
            | fields         | position_rating, firmware_version, firmware_upgrade, channel_state, channel_flags, channel_flags_manual    | start           | None                                                                                                                       |