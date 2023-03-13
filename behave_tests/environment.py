#!/usr/bin/env python3

"""
    Copyright 2022 carlkidcrypto, All rights reserved.
    Behavior driven tests for the purpleair_data_logger.
"""

from os import mkdir, path, getcwd, environ
from shutil import rmtree
from platform import python_version, system


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

    # Init vars used in behave steps
    context.test_settings_file_name = ""
    context.csvdatalogger_save_file_path = ""
    context.python_version_list = python_version().split(".")
    context.operating_system = system().lower()

    if "PAA_API_READ_KEY" in environ.keys():
        context.config.userdata["PAA_API_READ_KEY"] = ""
        context.config.userdata["PAA_API_READ_KEY"] = environ["PAA_API_READ_KEY"]

    if "PAA_API_WRITE_KEY" in environ.keys():
        context.config.userdata["PAA_API_WRITE_KEY"] = ""
        context.config.userdata["PAA_API_WRITE_KEY"] = environ["PAA_API_WRITE_KEY"]


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

    context.test_settings_file_name = ""
    context.csvdatalogger_save_file_path = ""


def after_scenario(context, scenario):
    """
    These run before and after each scenario is run.
    """

    context.test_settings_file_name = ""
    context.csvdatalogger_save_file_path = ""


def before_feature(context, feature):
    """
    These run before and after each feature file is exercised.
    """

    context.test_settings_file_name = ""
    context.csvdatalogger_save_file_path = ""


def after_feature(context, feature):
    """
    These run before and after each feature file is exercised.
    """

    context.test_settings_file_name = ""
    context.csvdatalogger_save_file_path = ""


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
