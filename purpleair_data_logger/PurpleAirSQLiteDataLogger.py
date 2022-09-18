#!/usr/bin/env python3

"""
    Copyright 2022 carlkid1499, All rights reserved.
    A python class designed to use the PurpleAirAPI for requesting sensor(s) data.
    Data will be inserted into a SQLite3 database file.
    
    For best practice from PurpleAir:
    "The data from individual sensors will update no less than every 30 seconds.
    As a courtesy, we ask that you limit the number of requests to no more than
    once every 1 to 10 minutes, assuming you are only using the API to obtain data
    from sensors. If retrieving data from multiple sensors at once, please send a
    single request rather than individual requests in succession."
"""

from purpleair_data_logger.PurpleAirDataLogger import PurpleAirDataLogger
import argparse
import json


class PurpleAirSQLiteDataLogger(PurpleAirDataLogger):
    """
        The logger class. For now we will insert data into a SQLite3 database file.
    """

    def __init__(self, PurpleAirAPIReadKey):
        """
            :param str PurpleAirAPIReadKey: A valid PurpleAirAPI Read key
        """

        # Inherit everything from the parent base class: PurpleAirDataLogger
        super().__init__(PurpleAirAPIReadKey)

    def store_sensor_data(self, single_sensor_data_dict):
        raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Collect data from PurpleAir sensors and store it a SQLite3 database file!")
    parser.add_argument("-save_file_path",  required=True,
                        dest="save_file_path", type=str, help="""The path to save CSV files in.""")
    parser.add_argument("-paa_read_key",  required=True,
                        dest="paa_read_key", type=str, help="""The PurpleAirAPI Read key""")
    parser.add_argument("-paa_single_sensor_request_json_file",  required=False, default=None,
                        dest="paa_single_sensor_request_json_file", type=str, help="""The
                        path to a json file containing the parameters to send a single
                        sensor request.""")
    parser.add_argument("-paa_multiple_sensor_request_json_file",  required=False, default=None,
                        dest="paa_multiple_sensor_request_json_file", type=str, help="""The
                        path to a json file containing the parameters to send a multiple
                        sensor request.""")

    args = parser.parse_args()

    # Place holders that are used later down
    the_json_file = None
    file_obj = None

    # Second make an instance our our data logger
    the_paa_csv_data_logger = PurpleAirSQLiteDataLogger(
        args.paa_read_key, args.save_file_path)

    # Third choose what run method to execute depending on paa_multiple_sensor_request_json_file/paa_single_sensor_request_json_file
    if args.paa_multiple_sensor_request_json_file is not None and args.paa_single_sensor_request_json_file is None:
        # Now load up that json file
        file_obj = open(args.paa_multiple_sensor_request_json_file, "r")
        the_json_file = json.load(file_obj)
        the_paa_csv_data_logger.run_loop_for_storing_multiple_sensors_data(
            the_json_file)

    elif args.paa_multiple_sensor_request_json_file is None and args.paa_single_sensor_request_json_file is not None:
        # Now load up that json file
        file_obj = open(args.paa_single_sensor_request_json_file, "r")
        the_json_file = json.load(file_obj)
        the_paa_csv_data_logger.run_loop_for_storing_single_sensor_data(
            the_json_file)

    else:
        raise ValueError(
            """The parameter '-paa_multiple_sensor_request_json_file' or '-paa_single_sensor_request_json_file' must be provided. Not both.""")
