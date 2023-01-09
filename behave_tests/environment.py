#!/usr/bin/env python3

"""
    Copyright 2022 carlkid1499, All rights reserved.
    Behavior driven tests for the purpleair_data_logger.
"""

from os import mkdir, path, getcwd
from shutil import rmtree
from time import sleep

def before_all(context):
    """
        These run before and after the whole shooting match.
    """

    # Make a place to store logs. First remove then create
    current_directory = getcwd()
    try:
        rmtree(path.join(current_directory, "logs"))

    except FileNotFoundError:
        # Do nothing
        pass
    
    except OSError as os_err:
        if os_err.errno == 39:
            # Directory is not empty
            pass

        else:
            raise

    mkdir(path.join(current_directory, "logs"))

    # Save off logs path
    context.logs_path = getcwd() + "/logs"

def after_all(context):
    """
        These run before and after the whole shooting match.
    """
    pass


def before_step(context, step):
    """
        These run before and after every step.
    """
    pass


def after_step(context, step):
    """
        These run before and after every step.
    """
    pass
        


def before_scenario(context, scenario):
    """
        These run before and after each scenario is run.
    """
    pass


def after_scenario(context, scenario):
    """
        These run before and after each scenario is run.
    """
    pass


def before_feature(context, feature):
    """
        These run before and after each feature file is exercised.
    """
    pass


def after_feature(context, feature):
    """
        These run before and after each feature file is exercised.
    """
    pass


def before_tag(context, tag):
    """
        These run before and after a section tagged with the given name.
        They are invoked for each tag encountered in the order they’re found in the feature file.
        See controlling things with tags.
    """
    pass


def after_tag(context, tag):
    """
        These run before and after a section tagged with the given name.
        They are invoked for each tag encountered in the order they’re found in the feature file.
        See controlling things with tags.
    """
    pass
