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
        Then the CSVDatalogger should not start

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