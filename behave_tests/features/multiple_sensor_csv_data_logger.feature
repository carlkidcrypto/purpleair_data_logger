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

        