###############################################################################
# Copyright 2022 carlkid1499, All rights reserved.
# Behavior driven tests for the purpleair_data_logger.
# This file will test the Behavior for the CSVDatalogger when a
# multiple sensor configuration file is passed in
###############################################################################

Feature: CSVDatalogger when a multiple sensor configuration file is passed in

    Scenario Outline: An invalid configuration file is provided
        Given we do not provide <field> in configuration file
        When we start the CSVDatalogger using above configuration file
        Then the CSVDatalogger should fail to start

        Examples: Missing configuration settings
            | field          |
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

    Scenario Outline: A valid configuration file is provided
        Given we do provide <field> in configuration file with <value>
        When we start the CSVDatalogger using above configuration file
        Then the CSVDatalogger should <expected result> successfully

        Examples: Test 'fields' configuration settings
            | field          | value                                                                                                      | expected result |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
            | fields         | null                                                                                                       | not start       |
            | fields         | name                                                                                                       | start           |
            | fields         | position_rating, firmware_version, firmware_upgrade, channel_state, channel_flags, channel_flags_manual    | start           |
            | location_type  | null                                                                                                       | start           |
            | read_keys      | null                                                                                                       | start           |
            | show_only      | null                                                                                                       | start           |
            | modified_since | null                                                                                                       | start           |
            | max_age        | null                                                                                                       | start           |
            | nwlng          | null                                                                                                       | start           |
            | nwlat          | null                                                                                                       | start           |
            | selng          | null                                                                                                       | start           |
            | selat          | null                                                                                                       | start           |