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
from purpleair_data_logger.PurpleAirSQLiteQueryStatements import (
    SQLITE_INSERT_STATEMENT_ENVIRONMENTAL_FIELDS,
    SQLITE_INSERT_STATEMENT_MISCELLANEOUS_FIELDS,
    SQLITE_INSERT_STATEMENT_PARTICLE_COUNT_FIELDS,
    SQLITE_INSERT_STATEMENT_PM10_0_FIELDS,
    SQLITE_INSERT_STATEMENT_PM1_0_FIELDS,
    SQLITE_INSERT_STATEMENT_PM2_5_FIELDS,
    SQLITE_INSERT_STATEMENT_PM2_5_PSEUDO_AVERAGE_FIELDS,
    SQLITE_INSERT_STATEMENT_STATION_INFORMATION_AND_STATUS_FIELDS,
    SQLITE_INSERT_STATEMENT_THINGSPEAK_FIELDS,
    CREATE_PARTICLE_COUNT_FIELDS,
    CREATE_PM10_0_FIELDS,
    CREATE_PM1_0_FIELDS,
    CREATE_PM2_5_FIELDS,
    CREATE_PM2_5_PSEUDO_AVERAGE_FIELDS,
    CREATE_ENVIRONMENTAL_FIELDS_TABLE,
    CREATE_MISCELLANEOUS_FIELDS,
    CREATE_STATION_INFORMATION_AND_STATUS_FIELDS_TABLE,
    CREATE_THINGSPEAK_FIELDS,
    SQLITE_DROP_ALL_TABLES,
)
import argparse
import sqlite3


class PurpleAirSQLiteDataLogger(PurpleAirDataLogger):
    """
    The logger class. For now we will insert data into a SQLite3 database file.
    """

    def __init__(self, PurpleAirAPIReadKey, sqlite_data_base_name):
        """
        :param str PurpleAirAPIReadKey: A valid PurpleAirAPI Read key
        """

        # Inherit everything from the parent base class: PurpleAirDataLogger
        super().__init__(PurpleAirAPIReadKey)

        self._db_conn = sqlite3.connect(sqlite_data_base_name)

        # Make our PSQL Tables
        self._create_sqlite_db_tables()

    def _create_sqlite_db_tables(self):
        """
        Create the SQLITE database tables if they don't exist already

        We will create one table for different data groups. Simply following the
        official PurpleAir documentation. Think Station information and status fields,
        Environmental fields, etc. See website for more information.
        https://api.purpleair.com/#api-sensors-get-sensor-data
        """

        self._db_conn.execute(CREATE_STATION_INFORMATION_AND_STATUS_FIELDS_TABLE)
        self._db_conn.execute(CREATE_ENVIRONMENTAL_FIELDS_TABLE)
        self._db_conn.execute(CREATE_MISCELLANEOUS_FIELDS)
        self._db_conn.execute(CREATE_PM1_0_FIELDS)
        self._db_conn.execute(CREATE_PM2_5_FIELDS)
        self._db_conn.execute(CREATE_PM2_5_PSEUDO_AVERAGE_FIELDS)
        self._db_conn.execute(CREATE_PM10_0_FIELDS)
        self._db_conn.execute(CREATE_PARTICLE_COUNT_FIELDS)
        self._db_conn.execute(CREATE_THINGSPEAK_FIELDS)

    def store_sensor_data(self, single_sensor_data_dict):
        """
        Insert the sensor data into the database.

        :param dict single_sensor_data_dict: A python dictionary containing all fields
                                             for insertion. If a sensor doesn't support
                                             a certain field make sure it is NULL and part
                                             of the dictionary. This method does no type
                                             or error checking. That is upto the caller.
        """

        # Run the queries
        self._db_conn.execute(
            SQLITE_INSERT_STATEMENT_STATION_INFORMATION_AND_STATUS_FIELDS,
            (
                single_sensor_data_dict["data_time_stamp"],
                single_sensor_data_dict["sensor_index"],
                single_sensor_data_dict["name"],
                single_sensor_data_dict["icon"],
                single_sensor_data_dict["model"],
                single_sensor_data_dict["hardware"],
                single_sensor_data_dict["location_type"],
                single_sensor_data_dict["private"],
                single_sensor_data_dict["latitude"],
                single_sensor_data_dict["longitude"],
                single_sensor_data_dict["altitude"],
                single_sensor_data_dict["position_rating"],
                single_sensor_data_dict["led_brightness"],
                single_sensor_data_dict["firmware_version"],
                single_sensor_data_dict["firmware_upgrade"],
                single_sensor_data_dict["rssi"],
                single_sensor_data_dict["uptime"],
                single_sensor_data_dict["pa_latency"],
                single_sensor_data_dict["memory"],
                single_sensor_data_dict["last_seen"],
                single_sensor_data_dict["last_modified"],
                single_sensor_data_dict["date_created"],
                single_sensor_data_dict["channel_state"],
                single_sensor_data_dict["channel_flags"],
                single_sensor_data_dict["channel_flags_manual"],
                single_sensor_data_dict["channel_flags_auto"],
                single_sensor_data_dict["confidence"],
                single_sensor_data_dict["confidence_manual"],
                single_sensor_data_dict["confidence_auto"],
            ),
        )

        self._db_conn.execute(
            SQLITE_INSERT_STATEMENT_ENVIRONMENTAL_FIELDS,
            (
                single_sensor_data_dict["data_time_stamp"],
                single_sensor_data_dict["sensor_index"],
                single_sensor_data_dict["humidity"],
                single_sensor_data_dict["humidity_a"],
                single_sensor_data_dict["humidity_b"],
                single_sensor_data_dict["temperature"],
                single_sensor_data_dict["temperature_a"],
                single_sensor_data_dict["temperature_b"],
                single_sensor_data_dict["pressure"],
                single_sensor_data_dict["pressure_a"],
                single_sensor_data_dict["pressure_b"],
            ),
        )

        self._db_conn.execute(
            SQLITE_INSERT_STATEMENT_MISCELLANEOUS_FIELDS,
            (
                single_sensor_data_dict["data_time_stamp"],
                single_sensor_data_dict["sensor_index"],
                single_sensor_data_dict["voc"],
                single_sensor_data_dict["voc_a"],
                single_sensor_data_dict["voc_b"],
                single_sensor_data_dict["ozone1"],
                single_sensor_data_dict["analog_input"],
            ),
        )

        self._db_conn.execute(
            SQLITE_INSERT_STATEMENT_PM1_0_FIELDS,
            (
                single_sensor_data_dict["data_time_stamp"],
                single_sensor_data_dict["sensor_index"],
                single_sensor_data_dict["pm1.0"],
                single_sensor_data_dict["pm1.0_a"],
                single_sensor_data_dict["pm1.0_b"],
                single_sensor_data_dict["pm1.0_atm"],
                single_sensor_data_dict["pm1.0_atm_a"],
                single_sensor_data_dict["pm1.0_atm_b"],
                single_sensor_data_dict["pm1.0_cf_1"],
                single_sensor_data_dict["pm1.0_cf_1_a"],
                single_sensor_data_dict["pm1.0_cf_1_b"],
            ),
        )

        self._db_conn.execute(
            SQLITE_INSERT_STATEMENT_PM2_5_FIELDS,
            (
                single_sensor_data_dict["data_time_stamp"],
                single_sensor_data_dict["sensor_index"],
                single_sensor_data_dict["pm2.5_alt"],
                single_sensor_data_dict["pm2.5_alt_a"],
                single_sensor_data_dict["pm2.5_alt_b"],
                single_sensor_data_dict["pm2.5"],
                single_sensor_data_dict["pm2.5_a"],
                single_sensor_data_dict["pm2.5_b"],
                single_sensor_data_dict["pm2.5_atm"],
                single_sensor_data_dict["pm2.5_atm_a"],
                single_sensor_data_dict["pm2.5_atm_b"],
                single_sensor_data_dict["pm2.5_cf_1"],
                single_sensor_data_dict["pm2.5_cf_1_a"],
                single_sensor_data_dict["pm2.5_cf_1_b"],
            ),
        )

        self._db_conn.execute(
            SQLITE_INSERT_STATEMENT_PM2_5_PSEUDO_AVERAGE_FIELDS,
            (
                single_sensor_data_dict["data_time_stamp"],
                single_sensor_data_dict["sensor_index"],
                single_sensor_data_dict["pm2.5_10minute"],
                single_sensor_data_dict["pm2.5_10minute_a"],
                single_sensor_data_dict["pm2.5_10minute_b"],
                single_sensor_data_dict["pm2.5_30minute"],
                single_sensor_data_dict["pm2.5_30minute_a"],
                single_sensor_data_dict["pm2.5_30minute_b"],
                single_sensor_data_dict["pm2.5_60minute"],
                single_sensor_data_dict["pm2.5_60minute_a"],
                single_sensor_data_dict["pm2.5_60minute_b"],
                single_sensor_data_dict["pm2.5_6hour"],
                single_sensor_data_dict["pm2.5_6hour_a"],
                single_sensor_data_dict["pm2.5_6hour_b"],
                single_sensor_data_dict["pm2.5_24hour"],
                single_sensor_data_dict["pm2.5_24hour_a"],
                single_sensor_data_dict["pm2.5_24hour_b"],
                single_sensor_data_dict["pm2.5_1week"],
                single_sensor_data_dict["pm2.5_1week_a"],
                single_sensor_data_dict["pm2.5_1week_b"],
            ),
        )

        self._db_conn.execute(
            SQLITE_INSERT_STATEMENT_PM10_0_FIELDS,
            (
                single_sensor_data_dict["data_time_stamp"],
                single_sensor_data_dict["sensor_index"],
                single_sensor_data_dict["pm10.0"],
                single_sensor_data_dict["pm10.0_a"],
                single_sensor_data_dict["pm10.0_b"],
                single_sensor_data_dict["pm10.0_atm"],
                single_sensor_data_dict["pm10.0_atm_a"],
                single_sensor_data_dict["pm10.0_atm_b"],
                single_sensor_data_dict["pm10.0_cf_1"],
                single_sensor_data_dict["pm10.0_cf_1_a"],
                single_sensor_data_dict["pm10.0_cf_1_b"],
            ),
        )

        self._db_conn.execute(
            SQLITE_INSERT_STATEMENT_PARTICLE_COUNT_FIELDS,
            (
                single_sensor_data_dict["data_time_stamp"],
                single_sensor_data_dict["sensor_index"],
                single_sensor_data_dict["0.3_um_count"],
                single_sensor_data_dict["0.3_um_count_a"],
                single_sensor_data_dict["0.3_um_count_b"],
                single_sensor_data_dict["0.5_um_count"],
                single_sensor_data_dict["0.5_um_count_a"],
                single_sensor_data_dict["0.5_um_count_b"],
                single_sensor_data_dict["1.0_um_count"],
                single_sensor_data_dict["1.0_um_count_a"],
                single_sensor_data_dict["1.0_um_count_b"],
                single_sensor_data_dict["2.5_um_count"],
                single_sensor_data_dict["2.5_um_count_a"],
                single_sensor_data_dict["2.5_um_count_b"],
                single_sensor_data_dict["5.0_um_count"],
                single_sensor_data_dict["5.0_um_count_a"],
                single_sensor_data_dict["5.0_um_count_b"],
                single_sensor_data_dict["10.0_um_count"],
                single_sensor_data_dict["10.0_um_count_a"],
                single_sensor_data_dict["10.0_um_count_b"],
            ),
        )

        self._db_conn.execute(
            SQLITE_INSERT_STATEMENT_THINGSPEAK_FIELDS,
            (
                single_sensor_data_dict["data_time_stamp"],
                single_sensor_data_dict["sensor_index"],
                single_sensor_data_dict["primary_id_a"],
                single_sensor_data_dict["primary_key_a"],
                single_sensor_data_dict["secondary_id_a"],
                single_sensor_data_dict["secondary_key_a"],
                single_sensor_data_dict["primary_id_b"],
                single_sensor_data_dict["primary_key_b"],
                single_sensor_data_dict["secondary_id_b"],
                single_sensor_data_dict["secondary_key_b"],
            ),
        )

        # Commit to the db
        self._db_conn.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Collect data from PurpleAir sensors and store it a SQLite3 database file!"
    )
    parser.add_argument(
        "-db_name",
        required=True,
        dest="db_name",
        type=str,
        help="""The path and name for the SQLite3 database
                        file! i.e database_name.db""",
    )
    parser.add_argument(
        "-paa_read_key",
        required=True,
        dest="paa_read_key",
        type=str,
        help="""The PurpleAirAPI Read key""",
    )
    parser.add_argument(
        "-paa_single_sensor_request_json_file",
        required=False,
        default=None,
        dest="paa_single_sensor_request_json_file",
        type=str,
        help="""The
                        path to a json file containing the parameters to send a single
                        sensor request.""",
    )
    parser.add_argument(
        "-paa_multiple_sensor_request_json_file",
        required=False,
        default=None,
        dest="paa_multiple_sensor_request_json_file",
        type=str,
        help="""The
                        path to a json file containing the parameters to send a multiple
                        sensor request.""",
    )

    args = parser.parse_args()

    # Place holders that are used later down
    the_json_file = None
    file_obj = None

    # Second make an instance our our data logger
    the_paa_sqlite_data_logger = PurpleAirSQLiteDataLogger(
        args.paa_read_key, args.db_name
    )

    # Third choose what run method to execute depending on paa_multiple_sensor_request_json_file/paa_single_sensor_request_json_file
    the_paa_sqlite_data_logger.validate_parameters_and_run(
        args.paa_multiple_sensor_request_json_file,
        args.paa_single_sensor_request_json_file,
    )
