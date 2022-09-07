#!/usr/bin/env python3

"""
    Copyright 2022 carlkid1499, All rights reserved.
    A python class designed to use the PurpleAirAPI for requesting sensor(s) data.
    
    For best practice from PurpleAir:
    "The data from individual sensors will update no less than every 30 seconds.
    As a courtesy, we ask that you limit the number of requests to no more than
    once every 1 to 10 minutes, assuming you are only using the API to obtain data
    from sensors. If retrieving data from multiple sensors at once, please send a
    single request rather than individual requests in succession."
"""

from purpleair_data_logger.PurpleAirDataLogger import PurpleAirDataLogger
from os import makedirs
from os.path import exists

import argparse
import json


class PurpleAirCSVDataLogger(PurpleAirDataLogger):
    """
        The logger class. For now we will insert data into a CSV file.
    """

    def __init__(self, PurpleAirAPIReadKey, path_to_save_csv_files_in):
        """
            :param str PurpleAirAPIReadKey: A valid PurpleAirAPI Read key
            :param object psql_db_conn: A valid PG8000 database connection
        """

        # Inherit everything from the parent base class: PurpleAirDataLogger
        super().__init__(PurpleAirAPIReadKey)

        # save off the store path internally for later access
        self._path_to_save_csv_files_in = path_to_save_csv_files_in

        # Init some class vars
        self._did_we_write_the_header_bool = False

    def _open_csv_file(self, file_path_and_name):
        the_file_stream = open(file_path_and_name, "w")
        return the_file_stream

    def _close_and_flush_csv_file(self, the_file_stream):
        the_file_stream.flush()
        the_file_stream.close()

    def store_sensor_data(self, single_sensor_data_dict):
        """
            Insert the sensor data into the database.

            :param dict single_sensor_data_dict: A python dictionary containing all fields
                                                 for insertion. If a sensor doesn't support
                                                 a certain field make sure it is NULL and part
                                                 of the dictionary. This method does no type
                                                 or error checking. That is upto the caller.
        """

        # Step one make the self._path_to_save_csv_files_in if it doesn't exist already
        if exists(self._path_to_save_csv_files_in) == False:
            print(f"Creating storage directory: {self._path_to_save_csv_files_in}...")
            makedirs(self._path_to_save_csv_files_in)

        # Step two create all the unique files names
        
        # Step three write data to all files.
        raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Collect data from PurpleAir sensors and store it in CSV files!")
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
    the_paa_csv_data_logger = PurpleAirCSVDataLogger(
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
