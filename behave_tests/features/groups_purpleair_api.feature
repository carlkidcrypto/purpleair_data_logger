###############################################################################
# Copyright 2023 carlkid1499, All rights reserved.
# Behavior driven tests for the purpleair api module.
# This file will test the Behavior for `groups`
###############################################################################
@wip
Feature: Test the behvior of PurpleAirAPI methods that deal with `groups`

    Scenario: Test the `post_create_group_data` method
        Given we use the PurpleAirAPI module
        When we use the `post_create_group_data` method to create a group called: `Behave Test Group`
        Then the PurpleAirAPI should not raise any errors
        And the group `Behave Test Group` should be created
    
    Scenario: Test the `post_create_group_data` method