#!/usr/bin/env python3

"""
    Copyright 2023 carlkidcrypto, All rights reserved.
    A python class designed to use the PurpleAirAPI for requesting sensor(s) data.
    Data will be inserted into CSV files.
    
    For best practice from PurpleAir:
    "The data from individual sensors will update no less than every 30 seconds.
    As a courtesy, we ask that you limit the number of requests to no more than
    once every 1 to 10 minutes, assuming you are only using the API to obtain data
    from sensors. If retrieving data from multiple sensors at once, please send a
    single request rather than individual requests in succession."
"""

from purpleair_data_logger.PurpleAirDataLogger import (
    PurpleAirDataLogger,
)

from purpleair_data_logger.PurpleAirDataLoggerHelpers import (
    generate_common_arg_parser,
)


from purpleair_data_logger.PurpleAirCSVDataLoggerConstants import (
    STATION_INFORMATION_AND_STATUS_FIELDS_FILE_NAME,
    STATION_INFORMATION_AND_STATUS_FIELDS_HEADER,
    ENVIRONMENTAL_FIELDS_FILE_NAME,
    ENVIRONMENTAL_FIELDS_HEADER,
    MISCELLANEOUS_FIELDS_FILE_NAME,
    MISCELLANEOUS_FIELDS_HEADER,
    PM1_0_FIELDS_FILE_NAME,
    PM1_0_FIELDS_HEADER,
    PM2_5_FIELDS_FILE_NAME,
    PM2_5_FIELDS_HEADER,
    PM2_5_PSEUDO_AVERAGE_FIELDS_FILE_NAME,
    PM2_5_PSEUDO_AVERAGE_FIELDS_HEADER,
    PM10_0_FIELDS_FILE_NAME,
    PM10_0_FIELDS_HEADER,
    PARTICLE_COUNT_FIELDS_FILE_NAME,
    PARTICLE_COUNT_FIELDS_HEADER,
    THINGSPEAK_FIELDS_FILE_NAME,
    THINGSPEAK_FIELDS_HEADER,
)
from os import makedirs
from os.path import exists


class PurpleAirCSVDataLogger(PurpleAirDataLogger):
    """
    The logger class. For now we will insert data into a CSV file.
    """

    def __init__(
        self,
        PurpleAirApiReadKey=None,
        PurpleAirApiWriteKey=None,
        PurpleAirApiIpv4Address=None,
        path_to_save_csv_files_in=None,
    ):
        """
        :param str PurpleAirApiReadKey: A valid PurpleAirAPI Read key
        :param str PurpleAirApiWriteKey: A valid PurpleAirAPI Write key
        :param list PurpleAirApiIpv4Address: A list of valid IPv4 string addresses with no CIDR's.
        :param object path_to_save_csv_files_in: A string directory path
                                                 to save files in.
        """

        # Inherit everything from the parent base class: PurpleAirDataLogger
        super().__init__(
            PurpleAirApiReadKey, PurpleAirApiWriteKey, PurpleAirApiIpv4Address
        )

        # save off the store path internally for later access
        self._path_to_save_csv_files_in = path_to_save_csv_files_in

        # Init some class vars
        self._did_we_write_the_header_bool = False
        self._data_error_counter = 0

    @staticmethod
    def _open_csv_file(file_path_and_name):
        """
        Create the given 'file_path_and_name'.

        :param str file_path_and_name: A string of 'file_path_and_name'. i.e
                                       '/path_to_place/file_name.csv'.
        """
        the_file_stream = open(file_path_and_name, "a")
        return the_file_stream

    @staticmethod
    def _close_and_flush_csv_file(the_file_stream):
        """
        Close and flush the given 'the_file_stream'.

        :param file_stream the_file_stream: An open file stream to flush and close.
        """
        the_file_stream.flush()
        the_file_stream.close()

    def store_sensor_data(self, single_sensor_data_dict):
        """
        Insert the sensor data into CSV files.

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

        try:
            # Step two create all the unique files names
            station_information_and_status_fields_file_stream = self._open_csv_file(
                self._path_to_save_csv_files_in
                + "/"
                + STATION_INFORMATION_AND_STATUS_FIELDS_FILE_NAME
            )

            environmental_fields_file_steam = self._open_csv_file(
                self._path_to_save_csv_files_in + "/" + ENVIRONMENTAL_FIELDS_FILE_NAME
            )

            miscellaneous_fields_file_stream = self._open_csv_file(
                self._path_to_save_csv_files_in + "/" + MISCELLANEOUS_FIELDS_FILE_NAME
            )

            pm1_0_fields_file_stream = self._open_csv_file(
                self._path_to_save_csv_files_in + "/" + PM1_0_FIELDS_FILE_NAME
            )

            pm2_5_fields_file_stream = self._open_csv_file(
                self._path_to_save_csv_files_in + "/" + PM2_5_FIELDS_FILE_NAME
            )

            pm2_5_pseudo_average_fields_file_stream = self._open_csv_file(
                self._path_to_save_csv_files_in
                + "/"
                + PM2_5_PSEUDO_AVERAGE_FIELDS_FILE_NAME
            )

            pm10_0_fields_file_stream = self._open_csv_file(
                self._path_to_save_csv_files_in + "/" + PM10_0_FIELDS_FILE_NAME
            )

            particle_count_fields_file_stream = self._open_csv_file(
                self._path_to_save_csv_files_in + "/" + PARTICLE_COUNT_FIELDS_FILE_NAME
            )

            thingspeak_fields_file_stream = self._open_csv_file(
                self._path_to_save_csv_files_in + "/" + THINGSPEAK_FIELDS_FILE_NAME
            )

            if self._did_we_write_the_header_bool == False:
                # Write the headers
                station_information_and_status_fields_file_stream.write(
                    STATION_INFORMATION_AND_STATUS_FIELDS_HEADER + "\n"
                )

                environmental_fields_file_steam.write(
                    ENVIRONMENTAL_FIELDS_HEADER + "\n"
                )

                miscellaneous_fields_file_stream.write(
                    MISCELLANEOUS_FIELDS_HEADER + "\n"
                )

                pm1_0_fields_file_stream.write(PM1_0_FIELDS_HEADER + "\n")

                pm2_5_fields_file_stream.write(PM2_5_FIELDS_HEADER + "\n")

                pm2_5_pseudo_average_fields_file_stream.write(
                    PM2_5_PSEUDO_AVERAGE_FIELDS_HEADER + "\n"
                )

                pm10_0_fields_file_stream.write(PM10_0_FIELDS_HEADER + "\n")

                particle_count_fields_file_stream.write(
                    PARTICLE_COUNT_FIELDS_HEADER + "\n"
                )

                thingspeak_fields_file_stream.write(THINGSPEAK_FIELDS_HEADER + "\n")

                self._did_we_write_the_header_bool = True

            # Step three write data to all files.
            station_information_and_status_fields_file_stream.write(
                str(single_sensor_data_dict["data_time_stamp"])
                + ","
                + str(single_sensor_data_dict["sensor_index"])
                + ","
                + str(single_sensor_data_dict["name"])
                + ","
                + str(single_sensor_data_dict["icon"])
                + ","
                + str(single_sensor_data_dict["model"])
                + ","
                + str(single_sensor_data_dict["hardware"])
                + ","
                + str(single_sensor_data_dict["location_type"])
                + ","
                + str(single_sensor_data_dict["private"])
                + ","
                + str(single_sensor_data_dict["latitude"])
                + ","
                + str(single_sensor_data_dict["longitude"])
                + ","
                + str(single_sensor_data_dict["altitude"])
                + ","
                + str(single_sensor_data_dict["position_rating"])
                + ","
                + str(single_sensor_data_dict["led_brightness"])
                + ","
                + str(single_sensor_data_dict["firmware_version"])
                + ","
                + str(single_sensor_data_dict["firmware_upgrade"])
                + ","
                + str(single_sensor_data_dict["rssi"])
                + ","
                + str(single_sensor_data_dict["uptime"])
                + ","
                + str(single_sensor_data_dict["pa_latency"])
                + ","
                + str(single_sensor_data_dict["memory"])
                + ","
                + str(single_sensor_data_dict["last_seen"])
                + ","
                + str(single_sensor_data_dict["last_modified"])
                + ","
                + str(single_sensor_data_dict["date_created"])
                + ","
                + str(single_sensor_data_dict["channel_state"])
                + ","
                + str(single_sensor_data_dict["channel_flags"])
                + ","
                + str(single_sensor_data_dict["channel_flags_manual"])
                + ","
                + str(single_sensor_data_dict["channel_flags_auto"])
                + ","
                + str(single_sensor_data_dict["confidence"])
                + ","
                + str(single_sensor_data_dict["confidence_manual"])
                + ","
                + str(single_sensor_data_dict["confidence_auto"])
                + "\n"
            )

            environmental_fields_file_steam.write(
                str(single_sensor_data_dict["data_time_stamp"])
                + ","
                + str(single_sensor_data_dict["sensor_index"])
                + ","
                + str(single_sensor_data_dict["humidity"])
                + ","
                + str(single_sensor_data_dict["humidity_a"])
                + ","
                + str(single_sensor_data_dict["humidity_b"])
                + ","
                + str(single_sensor_data_dict["temperature"])
                + ","
                + str(single_sensor_data_dict["temperature_a"])
                + ","
                + str(single_sensor_data_dict["temperature_b"])
                + ","
                + str(single_sensor_data_dict["pressure"])
                + ","
                + str(single_sensor_data_dict["pressure_a"])
                + ","
                + str(single_sensor_data_dict["pressure_b"])
                + "\n"
            )

            miscellaneous_fields_file_stream.write(
                str(single_sensor_data_dict["data_time_stamp"])
                + ","
                + str(single_sensor_data_dict["sensor_index"])
                + ","
                + str(single_sensor_data_dict["voc"])
                + ","
                + str(single_sensor_data_dict["voc_a"])
                + ","
                + str(single_sensor_data_dict["voc_b"])
                + ","
                + str(single_sensor_data_dict["ozone1"])
                + ","
                + str(single_sensor_data_dict["analog_input"])
                + "\n"
            )

            pm1_0_fields_file_stream.write(
                str(single_sensor_data_dict["data_time_stamp"])
                + ","
                + str(single_sensor_data_dict["sensor_index"])
                + ","
                + str(single_sensor_data_dict["pm1.0"])
                + ","
                + str(single_sensor_data_dict["pm1.0_a"])
                + ","
                + str(single_sensor_data_dict["pm1.0_b"])
                + ","
                + str(single_sensor_data_dict["pm1.0_atm"])
                + ","
                + str(single_sensor_data_dict["pm1.0_atm_a"])
                + ","
                + str(single_sensor_data_dict["pm1.0_atm_b"])
                + ","
                + str(single_sensor_data_dict["pm1.0_cf_1"])
                + ","
                + str(single_sensor_data_dict["pm1.0_cf_1_a"])
                + ","
                + str(single_sensor_data_dict["pm1.0_cf_1_b"])
                + "\n"
            )

            pm2_5_fields_file_stream.write(
                str(single_sensor_data_dict["data_time_stamp"])
                + ","
                + str(single_sensor_data_dict["sensor_index"])
                + ","
                + str(single_sensor_data_dict["pm2.5_alt"])
                + ","
                + str(single_sensor_data_dict["pm2.5_alt_a"])
                + ","
                + str(single_sensor_data_dict["pm2.5_alt_b"])
                + ","
                + str(single_sensor_data_dict["pm2.5"])
                + ","
                + str(single_sensor_data_dict["pm2.5_a"])
                + ","
                + str(single_sensor_data_dict["pm2.5_b"])
                + ","
                + str(single_sensor_data_dict["pm2.5_atm"])
                + ","
                + str(single_sensor_data_dict["pm2.5_atm_a"])
                + ","
                + str(single_sensor_data_dict["pm2.5_atm_b"])
                + ","
                + str(single_sensor_data_dict["pm2.5_cf_1"])
                + ","
                + str(single_sensor_data_dict["pm2.5_cf_1_a"])
                + ","
                + str(single_sensor_data_dict["pm2.5_cf_1_b"])
                + "\n"
            )

            pm2_5_pseudo_average_fields_file_stream.write(
                str(single_sensor_data_dict["data_time_stamp"])
                + ","
                + str(single_sensor_data_dict["sensor_index"])
                + ","
                + str(single_sensor_data_dict["pm2.5_10minute"])
                + ","
                + str(single_sensor_data_dict["pm2.5_10minute_a"])
                + ","
                + str(single_sensor_data_dict["pm2.5_10minute_b"])
                + ","
                + str(single_sensor_data_dict["pm2.5_30minute"])
                + ","
                + str(single_sensor_data_dict["pm2.5_30minute_a"])
                + ","
                + str(single_sensor_data_dict["pm2.5_30minute_b"])
                + ","
                + str(single_sensor_data_dict["pm2.5_60minute"])
                + ","
                + str(single_sensor_data_dict["pm2.5_60minute_a"])
                + ","
                + str(single_sensor_data_dict["pm2.5_60minute_b"])
                + ","
                + str(single_sensor_data_dict["pm2.5_6hour"])
                + ","
                + str(single_sensor_data_dict["pm2.5_6hour_a"])
                + ","
                + str(single_sensor_data_dict["pm2.5_6hour_b"])
                + ","
                + str(single_sensor_data_dict["pm2.5_24hour"])
                + ","
                + str(single_sensor_data_dict["pm2.5_24hour_a"])
                + ","
                + str(single_sensor_data_dict["pm2.5_24hour_b"])
                + ","
                + str(single_sensor_data_dict["pm2.5_1week"])
                + ","
                + str(single_sensor_data_dict["pm2.5_1week_a"])
                + ","
                + str(single_sensor_data_dict["pm2.5_1week_b"])
                + "\n"
            )

            pm10_0_fields_file_stream.write(
                str(single_sensor_data_dict["data_time_stamp"])
                + ","
                + str(single_sensor_data_dict["sensor_index"])
                + ","
                + str(single_sensor_data_dict["pm10.0"])
                + ","
                + str(single_sensor_data_dict["pm10.0_a"])
                + ","
                + str(single_sensor_data_dict["pm10.0_b"])
                + ","
                + str(single_sensor_data_dict["pm10.0_atm"])
                + ","
                + str(single_sensor_data_dict["pm10.0_atm_a"])
                + ","
                + str(single_sensor_data_dict["pm10.0_atm_b"])
                + ","
                + str(single_sensor_data_dict["pm10.0_cf_1"])
                + ","
                + str(single_sensor_data_dict["pm10.0_cf_1_a"])
                + ","
                + str(single_sensor_data_dict["pm10.0_cf_1_b"])
                + "\n"
            )

            particle_count_fields_file_stream.write(
                str(single_sensor_data_dict["data_time_stamp"])
                + ","
                + str(single_sensor_data_dict["sensor_index"])
                + ","
                + str(single_sensor_data_dict["0.3_um_count"])
                + ","
                + str(single_sensor_data_dict["0.3_um_count_a"])
                + ","
                + str(single_sensor_data_dict["0.3_um_count_b"])
                + ","
                + str(single_sensor_data_dict["0.5_um_count"])
                + ","
                + str(single_sensor_data_dict["0.5_um_count_a"])
                + ","
                + str(single_sensor_data_dict["0.5_um_count_b"])
                + ","
                + str(single_sensor_data_dict["1.0_um_count"])
                + ","
                + str(single_sensor_data_dict["1.0_um_count_a"])
                + ","
                + str(single_sensor_data_dict["1.0_um_count_b"])
                + ","
                + str(single_sensor_data_dict["2.5_um_count"])
                + ","
                + str(single_sensor_data_dict["2.5_um_count_a"])
                + ","
                + str(single_sensor_data_dict["2.5_um_count_b"])
                + ","
                + str(single_sensor_data_dict["5.0_um_count"])
                + ","
                + str(single_sensor_data_dict["5.0_um_count_a"])
                + ","
                + str(single_sensor_data_dict["5.0_um_count_b"])
                + ","
                + str(single_sensor_data_dict["10.0_um_count"])
                + ","
                + str(single_sensor_data_dict["10.0_um_count_a"])
                + ","
                + str(single_sensor_data_dict["10.0_um_count_b"])
                + "\n"
            )

            thingspeak_fields_file_stream.write(
                str(single_sensor_data_dict["data_time_stamp"])
                + ","
                + str(single_sensor_data_dict["sensor_index"])
                + ","
                + str(single_sensor_data_dict["primary_id_a"])
                + ","
                + str(single_sensor_data_dict["primary_key_a"])
                + ","
                + str(single_sensor_data_dict["secondary_id_a"])
                + ","
                + str(single_sensor_data_dict["secondary_key_a"])
                + ","
                + str(single_sensor_data_dict["primary_id_b"])
                + ","
                + str(single_sensor_data_dict["primary_key_b"])
                + ","
                + str(single_sensor_data_dict["secondary_id_b"])
                + ","
                + str(single_sensor_data_dict["secondary_key_b"])
                + "\n"
            )

        except UnicodeEncodeError as except_err:
            self._data_error_counter = self._data_error_counter + 1
            print("We weren't able to write the current data!")
            print(f"Data error counter is at {self._data_error_counter}")
            print(f"Error is {except_err} \n")

        self._close_and_flush_csv_file(
            station_information_and_status_fields_file_stream
        )
        self._close_and_flush_csv_file(environmental_fields_file_steam)
        self._close_and_flush_csv_file(miscellaneous_fields_file_stream)
        self._close_and_flush_csv_file(pm1_0_fields_file_stream)
        self._close_and_flush_csv_file(pm2_5_fields_file_stream)
        self._close_and_flush_csv_file(pm2_5_pseudo_average_fields_file_stream)
        self._close_and_flush_csv_file(pm10_0_fields_file_stream)
        self._close_and_flush_csv_file(particle_count_fields_file_stream)
        self._close_and_flush_csv_file(thingspeak_fields_file_stream)


if __name__ == "__main__":
    parser = generate_common_arg_parser(
        "Collect data from PurpleAir sensors and store it in CSV files!"
    )

    parser.add_argument(
        "-save_file_path",
        required=True,
        dest="save_file_path",
        type=str,
        help="""The path to save CSV files in.""",
    )

    args = parser.parse_args()

    # Place holders that are used later down
    the_json_file = None
    file_obj = None

    # Second make an instance our our data logger
    ipv4_address_list = []
    if args.paa_local_sensor_request_json_file:
        # This is a temp working solution. We will need to redo this at some point.
        import json

        file_obj = open(args.paa_local_sensor_request_json_file, "r")
        the_json_file = json.load(file_obj)
        file_obj.close()
        ipv4_address_list = the_json_file["sensor_ip_list"]  # LOAD THIS IN MAYBE ???
        del the_json_file

    the_paa_csv_data_logger = PurpleAirCSVDataLogger(
        args.paa_read_key, args.paa_write_key, ipv4_address_list, args.save_file_path
    )

    # Third choose what run method to execute depending on
    # paa_multiple_sensor_request_json_file/paa_single_sensor_request_json_file/paa_group_sensor_request_json_file
    the_paa_csv_data_logger.validate_parameters_and_run(
        args.paa_multiple_sensor_request_json_file,
        args.paa_single_sensor_request_json_file,
        args.paa_group_sensor_request_json_file,
        args.paa_local_sensor_request_json_file,
    )
