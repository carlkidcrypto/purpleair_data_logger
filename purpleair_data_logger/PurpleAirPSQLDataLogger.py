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

from purpleair_data_logger.PurpleAirAPI import PurpleAirAPI, debug_log
from purpleair_data_logger.PurpleAirAPIConstants import ACCEPTED_FIELD_NAMES_DICT
from purpleair_data_logger.PurpleAirPSQLQueryStatements import (PSQL_INSERT_STATEMENT_ENVIRONMENTAL_FIELDS, PSQL_INSERT_STATEMENT_MISCELLANEOUS_FIELDS,
                                          PSQL_INSERT_STATEMENT_PARTICLE_COUNT_FIELDS, PSQL_INSERT_STATEMENT_PM10_0_FIELDS,
                                          PSQL_INSERT_STATEMENT_PM1_0_FIELDS, PSQL_INSERT_STATEMENT_PM2_5_FIELDS,
                                          PSQL_INSERT_STATEMENT_PM2_5_PSEUDO_AVERAGE_FIELDS, PSQL_INSERT_STATEMENT_STATION_INFORMATION_AND_STATUS_FIELDS,
                                          PSQL_INSERT_STATEMENT_THINGSPEAK_FIELDS, CREATE_PARTICLE_COUNT_FIELDS,
                                          CREATE_PM10_0_FIELDS, CREATE_PM1_0_FIELDS, CREATE_PM2_5_FIELDS, CREATE_PM2_5_PSEUDO_AVERAGE_FIELDS,
                                          CREATE_ENVIRONMENTAL_FIELDS_TABLE, CREATE_MISCELLANEOUS_FIELDS, CREATE_STATION_INFORMATION_AND_STATUS_FIELDS_TABLE,
                                          CREATE_THINGSPEAK_FIELDS)
import pg8000
import argparse
from time import sleep
from datetime import datetime, timezone
import json


class PurpleAirDataLogger():
    """
        The logger class. For now we will ingest data into a TimeScaleDB PostgreSQL
        database. Then we will use Grafana to visualize said data.
    """

    def __init__(self, PurpleAirAPIReadKey, psql_db_conn):
        """
            :param str PurpleAirAPIReadKey: A valid PurpleAirAPI Read key
            :param object psql_db_conn: A valid PG8000 database connection
        """

        # Make one instance of our PurpleAirAPI class
        self.__paa_obj = PurpleAirAPI(PurpleAirAPIReadKey)

        # Make our psql database connection
        self.__db_conn = psql_db_conn

        # Make our PSQL Tables
        self.__create_psql_db_tables()

        # Convert our PSQL tables to hyper tables
        self.__convert_psql_tables_to_hyper_tables()

        # Create compression policies
        self.__configure_data_compression_policies()

        # Commit to the db
        self.__db_conn.commit()

        # Define how often we send requests
        self.__request_every_x = 65

    def __create_psql_db_tables(self):
        """
            Create the PSQL database tables if they don't exist already
        """

        # We will create one table for different data groups. Simply following the
        # offical PurpleAir documentaiton. Think Station information and status fields,
        # Environmental fields, etc. See website for more informaiton.
        # https://api.purpleair.com/#api-sensors-get-sensor-data

        self.__db_conn.run(CREATE_STATION_INFORMATION_AND_STATUS_FIELDS_TABLE)
        self.__db_conn.run(CREATE_ENVIRONMENTAL_FIELDS_TABLE)
        self.__db_conn.run(CREATE_MISCELLANEOUS_FIELDS)
        self.__db_conn.run(CREATE_PM1_0_FIELDS)
        self.__db_conn.run(CREATE_PM2_5_FIELDS)
        self.__db_conn.run(CREATE_PM2_5_PSEUDO_AVERAGE_FIELDS)
        self.__db_conn.run(CREATE_PM10_0_FIELDS)
        self.__db_conn.run(CREATE_PARTICLE_COUNT_FIELDS)
        self.__db_conn.run(CREATE_THINGSPEAK_FIELDS)

    def __convert_psql_tables_to_hyper_tables(self):
        """
            A method to convert our PSQL tables to TimeScaleDB hyper tables.
        """

        self.__db_conn.run(
            """SELECT create_hypertable('station_information_and_status_fields', 'data_time_stamp', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT create_hypertable('environmental_fields', 'data_time_stamp', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT create_hypertable('miscellaneous_fields', 'data_time_stamp', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT create_hypertable('pm1_0_fields', 'data_time_stamp', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT create_hypertable('pm2_5_fields', 'data_time_stamp', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT create_hypertable('pm2_5_pseudo_average_fields', 'data_time_stamp', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT create_hypertable('pm10_0_fields', 'data_time_stamp', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT create_hypertable('particle_count_fields', 'data_time_stamp', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT create_hypertable('thingspeak_fields', 'data_time_stamp', if_not_exists => TRUE)""")

    def __configure_data_compression_policies(self):
        """
            A method to set TimescaleDB data compression policies. More information
            can be found here: https://docs.timescale.com/api/latest/compression/add_compression_policy/#add-compression-policy
        """

        self.__db_conn.run(
            """ALTER TABLE station_information_and_status_fields SET (timescaledb.compress, timescaledb.compress_orderby = 'data_time_stamp',
                timescaledb.compress_segmentby = 'sensor_index')""")
        self.__db_conn.run(
            """ALTER TABLE environmental_fields SET (timescaledb.compress, timescaledb.compress_orderby = 'data_time_stamp',
                timescaledb.compress_segmentby = 'sensor_index')""")
        self.__db_conn.run(
            """ALTER TABLE miscellaneous_fields SET (timescaledb.compress, timescaledb.compress_orderby = 'data_time_stamp',
                timescaledb.compress_segmentby = 'sensor_index')""")
        self.__db_conn.run(
            """ALTER TABLE pm1_0_fields SET (timescaledb.compress, timescaledb.compress_orderby = 'data_time_stamp',
                timescaledb.compress_segmentby = 'sensor_index')""")
        self.__db_conn.run(
            """ALTER TABLE pm2_5_fields SET (timescaledb.compress, timescaledb.compress_orderby = 'data_time_stamp',
                timescaledb.compress_segmentby = 'sensor_index')""")
        self.__db_conn.run(
            """ALTER TABLE pm2_5_pseudo_average_fields SET (timescaledb.compress, timescaledb.compress_orderby = 'data_time_stamp',
                timescaledb.compress_segmentby = 'sensor_index')""")
        self.__db_conn.run(
            """ALTER TABLE pm10_0_fields SET (timescaledb.compress, timescaledb.compress_orderby = 'data_time_stamp',
                timescaledb.compress_segmentby = 'sensor_index')""")
        self.__db_conn.run(
            """ALTER TABLE particle_count_fields SET (timescaledb.compress, timescaledb.compress_orderby = 'data_time_stamp',
                timescaledb.compress_segmentby = 'sensor_index')""")
        self.__db_conn.run(
            """ALTER TABLE thingspeak_fields SET (timescaledb.compress, timescaledb.compress_orderby = 'data_time_stamp',
                timescaledb.compress_segmentby = 'sensor_index')""")

        self.__db_conn.run(
            """SELECT add_compression_policy('station_information_and_status_fields', INTERVAL '14d', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT add_compression_policy('environmental_fields', INTERVAL '14d', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT add_compression_policy('miscellaneous_fields', INTERVAL '14d', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT add_compression_policy('pm1_0_fields', INTERVAL '14d', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT add_compression_policy('pm2_5_fields', INTERVAL '14d', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT add_compression_policy('pm2_5_pseudo_average_fields', INTERVAL '14d', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT add_compression_policy('pm10_0_fields', INTERVAL '14d', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT add_compression_policy('particle_count_fields', INTERVAL '14d', if_not_exists => TRUE)""")
        self.__db_conn.run(
            """SELECT add_compression_policy('thingspeak_fields', INTERVAL '14d', if_not_exists => TRUE)""")

    def __convert_unix_epoch_timestamp_to_psql_timestamp(self, unix_epoch_timestamp):
        """
            A method to covert a unix epoch timestamp to a psql timestamp.

            :param int unix_epoch_timestamp: A valid unix epoch timestamp

            :return A valid psql UTC timestamp.
        """

        if unix_epoch_timestamp is None:
            return None

        else:
            return str(datetime.fromtimestamp(unix_epoch_timestamp, timezone.utc))

    def get_sensor_data(self, sensor_index, read_key=None, fields=None):
        """
            Request data from a single sensor.

            :param int sensor_index: A valid PurpleAirAPI sensor index.

            :param str read_key: A valid PurpleAirAPI private read key.

            :param str fields: A comma delmited string of valid field names.

            :return A python dictionary with data.
        """

        return self.__paa_obj.request_sensor_data(sensor_index, read_key, fields)

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
        self.__db_conn.run(
            PSQL_INSERT_STATEMENT_STATION_INFORMATION_AND_STATUS_FIELDS,
            data_time_stamp=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]),
            sensor_index=single_sensor_data_dict["sensor_index"],
            name=single_sensor_data_dict["name"],
            icon=single_sensor_data_dict["icon"],
            model=single_sensor_data_dict["model"],
            hardware=single_sensor_data_dict["hardware"],
            location_type=single_sensor_data_dict["location_type"],
            private=single_sensor_data_dict["private"],
            latitude=single_sensor_data_dict["latitude"],
            longitude=single_sensor_data_dict["longitude"],
            altitude=single_sensor_data_dict["altitude"],
            position_rating=single_sensor_data_dict["position_rating"],
            led_brightness=single_sensor_data_dict["led_brightness"],
            firmware_version=single_sensor_data_dict["firmware_version"],
            firmware_upgrade=single_sensor_data_dict["firmware_upgrade"],
            rssi=single_sensor_data_dict["rssi"],
            uptime=single_sensor_data_dict["uptime"],
            pa_latency=single_sensor_data_dict["pa_latency"],
            memory=single_sensor_data_dict["memory"],
            last_seen=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["last_seen"]),
            last_modified=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["last_modified"]),
            date_created=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["date_created"]),
            channel_state=single_sensor_data_dict["channel_state"],
            channel_flags=single_sensor_data_dict["channel_flags"],
            channel_flags_manual=single_sensor_data_dict["channel_flags_manual"],
            channel_flags_auto=single_sensor_data_dict["channel_flags_auto"],
            confidence=single_sensor_data_dict["confidence"],
            confidence_manual=single_sensor_data_dict["confidence_manual"],
            confidence_auto=single_sensor_data_dict["confidence_auto"]
        )

        self.__db_conn.run(
            PSQL_INSERT_STATEMENT_ENVIRONMENTAL_FIELDS,
            data_time_stamp=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]),
            sensor_index=single_sensor_data_dict["sensor_index"],
            humidity=single_sensor_data_dict["humidity"],
            humidity_a=single_sensor_data_dict["humidity_a"],
            humidity_b=single_sensor_data_dict["humidity_b"],
            temperature=single_sensor_data_dict["temperature"],
            temperature_a=single_sensor_data_dict["temperature_a"],
            temperature_b=single_sensor_data_dict["temperature_b"],
            pressure=single_sensor_data_dict["pressure"],
            pressure_a=single_sensor_data_dict["pressure_a"],
            pressure_b=single_sensor_data_dict["pressure_b"]
        )

        self.__db_conn.run(
            PSQL_INSERT_STATEMENT_MISCELLANEOUS_FIELDS,
            data_time_stamp=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]),
            sensor_index=single_sensor_data_dict["sensor_index"],
            voc=single_sensor_data_dict["voc"],
            voc_a=single_sensor_data_dict["voc_a"],
            voc_b=single_sensor_data_dict["voc_b"],
            ozone1=single_sensor_data_dict["ozone1"],
            analog_input=single_sensor_data_dict["analog_input"]
        )

        self.__db_conn.run(
            PSQL_INSERT_STATEMENT_PM1_0_FIELDS,
            data_time_stamp=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]),
            sensor_index=single_sensor_data_dict["sensor_index"],
            pm1_0=single_sensor_data_dict["pm1.0"],
            pm1_0_a=single_sensor_data_dict["pm1.0_a"],
            pm1_0_b=single_sensor_data_dict["pm1.0_b"],
            pm1_0_atm=single_sensor_data_dict["pm1.0_atm"],
            pm1_0_atm_a=single_sensor_data_dict["pm1.0_atm_a"],
            pm1_0_atm_b=single_sensor_data_dict["pm1.0_atm_b"],
            pm1_0_cf_1=single_sensor_data_dict["pm1.0_cf_1"],
            pm1_0_cf_1_a=single_sensor_data_dict["pm1.0_cf_1_a"],
            pm1_0_cf_1_b=single_sensor_data_dict["pm1.0_cf_1_b"]
        )

        self.__db_conn.run(
            PSQL_INSERT_STATEMENT_PM2_5_FIELDS,
            data_time_stamp=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]),
            sensor_index=single_sensor_data_dict["sensor_index"],
            pm2_5_alt=single_sensor_data_dict["pm2.5_alt"],
            pm2_5_alt_a=single_sensor_data_dict["pm2.5_alt_a"],
            pm2_5_alt_b=single_sensor_data_dict["pm2.5_alt_b"],
            pm2_5=single_sensor_data_dict["pm2.5"],
            pm2_5_a=single_sensor_data_dict["pm2.5_a"],
            pm2_5_b=single_sensor_data_dict["pm2.5_b"],
            pm2_5_atm=single_sensor_data_dict["pm2.5_atm"],
            pm2_5_atm_a=single_sensor_data_dict["pm2.5_atm_a"],
            pm2_5_atm_b=single_sensor_data_dict["pm2.5_atm_b"],
            pm2_5_cf_1=single_sensor_data_dict["pm2.5_cf_1"],
            pm2_5_cf_1_a=single_sensor_data_dict["pm2.5_cf_1_a"],
            pm2_5_cf_1_b=single_sensor_data_dict["pm2.5_cf_1_b"]
        )

        self.__db_conn.run(
            PSQL_INSERT_STATEMENT_PM2_5_PSEUDO_AVERAGE_FIELDS,
            data_time_stamp=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]),
            sensor_index=single_sensor_data_dict["sensor_index"],
            pm2_5_10minute=single_sensor_data_dict["pm2.5_10minute"],
            pm2_5_10minute_a=single_sensor_data_dict["pm2.5_10minute_a"],
            pm2_5_10minute_b=single_sensor_data_dict["pm2.5_10minute_b"],
            pm2_5_30minute=single_sensor_data_dict["pm2.5_30minute"],
            pm2_5_30minute_a=single_sensor_data_dict["pm2.5_30minute_a"],
            pm2_5_30minute_b=single_sensor_data_dict["pm2.5_30minute_b"],
            pm2_5_60minute=single_sensor_data_dict["pm2.5_60minute"],
            pm2_5_60minute_a=single_sensor_data_dict["pm2.5_60minute_a"],
            pm2_5_60minute_b=single_sensor_data_dict["pm2.5_60minute_b"],
            pm2_5_6hour=single_sensor_data_dict["pm2.5_6hour"],
            pm2_5_6hour_a=single_sensor_data_dict["pm2.5_6hour_a"],
            pm2_5_6hour_b=single_sensor_data_dict["pm2.5_6hour_b"],
            pm2_5_24hour=single_sensor_data_dict["pm2.5_24hour"],
            pm2_5_24hour_a=single_sensor_data_dict["pm2.5_24hour_a"],
            pm2_5_24hour_b=single_sensor_data_dict["pm2.5_24hour_b"],
            pm2_5_1week=single_sensor_data_dict["pm2.5_1week"],
            pm2_5_1week_a=single_sensor_data_dict["pm2.5_1week_a"],
            pm2_5_1week_b=single_sensor_data_dict["pm2.5_1week_b"]
        )

        self.__db_conn.run(
            PSQL_INSERT_STATEMENT_PM10_0_FIELDS,
            data_time_stamp=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]),
            sensor_index=single_sensor_data_dict["sensor_index"],
            pm10_0=single_sensor_data_dict["pm10.0"],
            pm10_0_a=single_sensor_data_dict["pm10.0_a"],
            pm10_0_b=single_sensor_data_dict["pm10.0_b"],
            pm10_0_atm=single_sensor_data_dict["pm10.0_atm"],
            pm10_0_atm_a=single_sensor_data_dict["pm10.0_atm_a"],
            pm10_0_atm_b=single_sensor_data_dict["pm10.0_atm_b"],
            pm10_0_cf_1=single_sensor_data_dict["pm10.0_cf_1"],
            pm10_0_cf_1_a=single_sensor_data_dict["pm10.0_cf_1_a"],
            pm10_0_cf_1_b=single_sensor_data_dict["pm10.0_cf_1_b"]
        )

        self.__db_conn.run(
            PSQL_INSERT_STATEMENT_PARTICLE_COUNT_FIELDS,
            data_time_stamp=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]),
            sensor_index=single_sensor_data_dict["sensor_index"],
            um_count_0_3=single_sensor_data_dict["0.3_um_count"],
            um_count_a_0_3=single_sensor_data_dict["0.3_um_count_a"],
            um_count_b_0_3=single_sensor_data_dict["0.3_um_count_b"],
            um_count_0_5=single_sensor_data_dict["0.5_um_count"],
            um_count_a_0_5=single_sensor_data_dict["0.5_um_count_a"],
            um_count_b_0_5=single_sensor_data_dict["0.5_um_count_b"],
            um_count_1_0=single_sensor_data_dict["1.0_um_count"],
            um_count_a_1_0=single_sensor_data_dict["1.0_um_count_a"],
            um_count_b_1_0=single_sensor_data_dict["1.0_um_count_b"],
            um_count_2_5=single_sensor_data_dict["2.5_um_count"],
            um_count_a_2_5=single_sensor_data_dict["2.5_um_count_a"],
            um_count_b_2_5=single_sensor_data_dict["2.5_um_count_b"],
            um_count_5_0=single_sensor_data_dict["5.0_um_count"],
            um_count_a_5_0=single_sensor_data_dict["5.0_um_count_a"],
            um_count_b_5_0=single_sensor_data_dict["5.0_um_count_b"],
            um_count_10_0=single_sensor_data_dict["10.0_um_count"],
            um_count_a_10_0=single_sensor_data_dict["10.0_um_count_a"],
            um_count_b_10_0=single_sensor_data_dict["10.0_um_count_b"]
        )

        self.__db_conn.run(
            PSQL_INSERT_STATEMENT_THINGSPEAK_FIELDS,
            data_time_stamp=self.__convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]),
            sensor_index=single_sensor_data_dict["sensor_index"],
            primary_id_a=single_sensor_data_dict["primary_id_a"],
            primary_key_a=single_sensor_data_dict["primary_key_a"],
            secondary_id_a=single_sensor_data_dict["secondary_id_a"],
            secondary_key_a=single_sensor_data_dict["secondary_key_a"],
            primary_id_b=single_sensor_data_dict["primary_id_b"],
            primary_key_b=single_sensor_data_dict["primary_key_b"],
            secondary_id_b=single_sensor_data_dict["secondary_id_b"],
            secondary_key_b=single_sensor_data_dict["secondary_key_b"]
        )

        # Commit to the db
        self.__db_conn.commit()

    def get_multiple_sensors_data(self, fields, location_type=None, read_keys=None, show_only=None, modified_since=None, max_age=None, nwlng=None, nwlat=None, selng=None, selat=None):
        """
            Request data from a multiple sensors. Uses the same parameters as
            PurpleAirAPI.request_multiple_sensors_data()

            :return A python dictionary with data.
        """

        return self.__paa_obj.request_multiple_sensors_data(fields, location_type, read_keys, show_only, modified_since, max_age, nwlng, nwlat, selng, selat)

    def store_multiple_sensors_data(self):
        """
            Insert the multiple sensors data into the database.
        """

        raise NotImplementedError

    def run_loop_for_storing_single_sensor_data(self, sensor_index):
        """
            A method containing the run loop for inserting a single sensors' data into the db.

            :param int sensor_index: A valid PurpleAirAPI sensor index.
        """

        while True:
            print("run_loop_for_storing_single_sensor_data - Beep boop I am alive...\n\n")
            # We will request data once every 65 seconds.
            debug_log(f"""Requesting new data from a sensor with index
                      {sensor_index}...""")

            sensor_data = self.get_sensor_data(sensor_index)

            # Let's make it easier on ourselves by making the sensor data one level deep.
            # Instead of json["sensor"]["KEYS..."] and json["sensor"]["stats_a"]["KEYS..."] etc
            # We turn it into just json["KEYS..."].
            the_modified_sensor_data = {}
            the_modified_sensor_data["data_time_stamp"] = sensor_data["data_time_stamp"]
            for key, val in sensor_data["sensor"].items():
                if key == "stats":
                    # For now name this one stats_pm2.5 until I understand the difference
                    # between sensor_data["stats"]["pm2.5"] and sensor_data["pm2.5"].
                    # Update 07/25/2022: Heard back from PurpleAir. They are the same.
                    the_modified_sensor_data["stats_pm2.5"] = val["pm2.5"]
                    the_modified_sensor_data["pm2.5_10minute"] = val["pm2.5_10minute"]
                    the_modified_sensor_data["pm2.5_30minute"] = val["pm2.5_30minute"]
                    the_modified_sensor_data["pm2.5_60minute"] = val["pm2.5_60minute"]
                    the_modified_sensor_data["pm2.5_6hour"] = val["pm2.5_6hour"]
                    the_modified_sensor_data["pm2.5_24hour"] = val["pm2.5_24hour"]
                    the_modified_sensor_data["pm2.5_1week"] = val["pm2.5_1week"]
                    the_modified_sensor_data["pm2.5_time_stamp"] = val["time_stamp"]

                elif key in ["stats_a", "stats_b"]:
                    the_modified_sensor_data[f"pm2.5_{key[-1]}"] = val["pm2.5"]
                    the_modified_sensor_data[f"pm2.5_10minute_{key[-1]}"] = val["pm2.5_10minute"]
                    the_modified_sensor_data[f"pm2.5_30minute_{key[-1]}"] = val["pm2.5_30minute"]
                    the_modified_sensor_data[f"pm2.5_60minute_{key[-1]}"] = val["pm2.5_60minute"]
                    the_modified_sensor_data[f"pm2.5_6hour_{key[-1]}"] = val["pm2.5_6hour"]
                    the_modified_sensor_data[f"pm2.5_24hour_{key[-1]}"] = val["pm2.5_24hour"]
                    the_modified_sensor_data[f"pm2.5_1week_{key[-1]}"] = val["pm2.5_1week"]
                    the_modified_sensor_data[f"time_stamp_{key[-1]}"] = val["time_stamp"]

                else:
                    the_modified_sensor_data[key] = val

            self.store_sensor_data(the_modified_sensor_data)
            debug_log(f"""Waiting {self.__request_every_x} seconds before
                  requesting new data again...""")
            sleep(self.__request_every_x)

    def run_loop_for_storing_multiple_sensors_data(self, json_config_file):
        """
            A method containing the run loop for inserting a multiple sensors' data into the db.

            :param dict json_config_file: A dictionary object of the json config file using json load.
        """

        while True:
            print(
                "run_loop_for_storing_multiple_sensors_data - Beep boop I am alive...\n\n")
            # We will request data once every 65 seconds.
            debug_log(f"""Requesting new data from multiple sensors with fields
                      {json_config_file["fields"]}...""")
            sensors_data = self.get_multiple_sensors_data(fields=json_config_file["fields"],
                                                          location_type=json_config_file["location_type"],
                                                          read_keys=json_config_file["read_keys"],
                                                          show_only=json_config_file["show_only"],
                                                          modified_since=json_config_file["modified_since"],
                                                          max_age=json_config_file["max_age"],
                                                          nwlng=json_config_file["nwlng"],
                                                          nwlat=json_config_file["nwlat"],
                                                          selng=json_config_file["selng"],
                                                          selat=json_config_file["selat"])

            # The sensors data will look something like this:
            # {'api_version': 'V1.0.11-0.0.34', 'time_stamp': 1659710288, 'data_time_stamp': 1659710232,
            # 'max_age': 604800, 'firmware_default_version': '7.00', 'fields': ['sensor_index', 'name'],
            # 'data': [[131075, 'Mariners Bluff'], [131079, 'BRSKBV-outside'], [131077, 'BEE Patio'],
            # ... ]}
            # It is important to know that the order of 'fields' provided as an argument to get_multiple_sensors_data()
            # will determine the order of data items. In a nutshell it is a 1:1 mapping from fields to data.
            # Now lets build and feed what the store_sensor_data() method expects.

            # Extract the 'fields' and 'data' parts to make it easier on ourselves
            extracted_fields = sensors_data["fields"]
            extracted_data = sensors_data["data"]

            # Grab each list of data items from extracted data
            for data_list in extracted_data:
                # Start making our modified sensor data object that will be passed to the
                # self.store_sensor_data() method
                the_modified_sensor_data = {}
                the_modified_sensor_data["data_time_stamp"] = sensors_data["data_time_stamp"]
                for data_index, data_item in enumerate(data_list):
                    the_modified_sensor_data[str(
                        extracted_fields[data_index])] = data_item

                # Before we store the data, we must make sure all fields have been included
                # Our psql store statements expect all fields regardless of what we request.
                for field in ACCEPTED_FIELD_NAMES_DICT.keys():
                    if field not in the_modified_sensor_data.keys():
                        the_modified_sensor_data[str(
                            field)] = ACCEPTED_FIELD_NAMES_DICT[field]

                # Store the current data
                self.store_sensor_data(the_modified_sensor_data)

            debug_log(f"""Waiting {self.__request_every_x} seconds before
                  requesting new data again...""")
            sleep(self.__request_every_x)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Collect data from PurpleAir sensors and insert into a database!")
    parser.add_argument("-db_usr",  required=True, dest="db_usr",
                        type=str, help="""The PSQL database user""")
    parser.add_argument("-db_host", required=False, default="localhost",
                        dest="db_host", type=str, help="""The PSQL database host""")
    parser.add_argument("-db", required=True, dest="db",
                        type=str, help="""The PSQL database name""")
    parser.add_argument("-db_port", required=False, default=5432,
                        dest="db_port", type=str, help="""The PSQL database port number""")
    parser.add_argument("-db_pwd",  required=False, default=None,
                        dest="db_pwd", type=str, help="""The PSQL database password""")
    parser.add_argument("-paa_read_key",  required=True,
                        dest="paa_read_key", type=str, help="""The PurpleAirAPI Read key""")
    parser.add_argument("-paa_sensor_index",  required=False,
                        dest="paa_sensor_index", type=int, help="""The PurpleAirAPI sensor index
                        for sending a single sensor request""")
    parser.add_argument("-paa_multiple_sensor_request_flag",  action="store_true", required=False,
                        dest="paa_multiple_sensor_request_flag", help="""This is a flag
                        that by default is false. When set to true, we expect a json config file with
                        parameters that will tell us how to format our multiple sensor request.""")
    parser.add_argument("-paa_multiple_sensor_request_json_file",  required=False,
                        dest="paa_multiple_sensor_request_json_file", type=str, help="""If
                        paa_multiple_sensor_request_flag is defined then this parameter is required.
                        It shall be the path to a json file containing the parameters to send a
                        multiple sensor request.""")

    args = parser.parse_args()

    # Place holders that are used later down
    the_json_file = None
    file_obj = None

    # First check for the paa_multiple_sensor_request_flag
    if args.paa_multiple_sensor_request_flag:
        # Then we must have paa_multiple_sensor_request_json_file as well
        if not args.paa_multiple_sensor_request_json_file:
            raise ValueError("""paa_multiple_sensor_request_json_file must be
                                provided when paa_multiple_sensor_request_flag is provided""")

        # Now load up that json file
        file_obj = open(args.paa_multiple_sensor_request_json_file, "r")
        the_json_file = json.load(file_obj)

    # Second make the PSQL DB connection with CML args
    the_psql_db_conn = pg8000.connect(
        user=args.db_usr,
        host=args.db_host,
        database=args.db,
        port=args.db_port,
        password=args.db_pwd)

    # Third make an instance our our data logger
    the_paa_data_logger = PurpleAirDataLogger(
        args.paa_read_key, the_psql_db_conn)

    # Fourth choose what run method to execute depending on paa_multiple_sensor_request_flag
    if args.paa_multiple_sensor_request_flag:
        the_paa_data_logger.run_loop_for_storing_multiple_sensors_data(
            the_json_file)

    else:
        the_paa_data_logger.run_loop_for_storing_single_sensor_data(
            args.paa_sensor_index)
