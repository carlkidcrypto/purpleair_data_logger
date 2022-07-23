#!/usr/bin/env python3

"""
    A python class designed to use the PurpleAirAPI for sensor data.
    For best practice from PurpleAir:
    "The data from individual sensors will update no less than every 30 seconds.
    As a courtesy, we ask that you limit the number of requests to no more than
    once every 1 to 10 minutes, assuming you are only using the API to obtain data
    from sensors. If retrieving data from multiple sensors at once, please send a
    single request rather than individual requests in succession."
"""

from PurpleAirAPI import PurpleAirAPI
import pg8000
import argparse
from time import sleep


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

    def __create_psql_db_tables(self):
        """
            Create the PSQL database tables if they don't exist already
        """

        # We will create one table for different data groups. Simply following the
        # offical PurpleAir documentaiton. Think Station information and status fields,
        # Environmental fields, etc. See website for more informaiton.
        # https://api.purpleair.com/#api-sensors-get-sensor-data

        # Generate the PSQL query strings. For simplicity our table names will match
        # what the PurpleAir documentation says. We will do the same for table column names.
        create_station_information_and_status_fields_table = """
            CREATE TABLE IF NOT EXISTS station_information_and_status_fields (
                data_time_stamp TIMESTAMP PRIMARY KEY,
                name TEXT,
                icon INT,
                model TEXT,
                hardware TEXT,
                location_type INT,
                private INT,
                latitude FLOAT,
                longitude FLOAT,
                altitude FLOAT,
                position_rating INT,
                led_brightness INT,
                firmware_version TEXT,
                firmware_upgrade TEXT,
                rssi INT,
                uptime INT,
                pa_latency INT,
                memory INT,
                last_seen TIMESTAMP,
                last_modified TIMESTAMP,
                date_created TIMESTAMP,
                channel_state INT,
                channel_flags INT,
                channel_flags_manual INT,
                channel_flags_auto INT,
                confidence INT,
                confidence_manual INT,
                confidence_auto INT)"""

        create_evironmental_fields_table = """
            CREATE TABLE IF NOT EXISTS evironmental_fields (
                data_time_stamp TIMESTAMP PRIMARY KEY,
                humidity INT,
                humidity_a INT,
                humidity_b INT,
                temperature INT,
                temperature_a INT,
                temperature_b INT,
                pressure FLOAT,
                pressure_a FLOAT,
                pressure_b FLOAT)"""

        create_miscellaneous_fields = """
            CREATE TABLE IF NOT EXISTS miscellaneous_fields (
                data_time_stamp TIMESTAMP PRIMARY KEY,
                voc FLOAT,
                voc_a FLOAT,
                voc_b FLOAT,
                ozone1 FLOAT,
                analog_input FLOAT)"""

        # Since we can't have decimals in variable names, we do pm1_0 instead of pm1.0
        create_pm10_fields = """
            CREATE TABLE IF NOT EXISTS pm10_fields(
                data_time_stamp TIMESTAMP PRIMARY KEY,
                pm1_0 FLOAT,
                pm1_0_a FLOAT,
                pm1_0_b FLOAT,
                pm1_0_atm FLOAT,
                pm1_0_atm_a FLOAT,
                pm1_0_atm_b FLOAT,
                pm1_0_cf_1 FLOAT,
                pm1_0_cf_1_a FLOAT,
                pm1_0_cf_1_b FLOAT)"""

        # Since we can't have decimals in variable names, we do pm2_5 instead of pm2.5
        create_pm25_fields = """
            CREATE TABLE IF NOT EXISTS pm25_fields (
                data_time_stamp TIMESTAMP PRIMARY KEY,
                pm2_5_alt FLOAT,
                pm2_5_alt_a FLOAT,
                pm2_5_alt_b FLOAT,
                pm2_5 FLOAT,
                pm2_5_a FLOAT,
                pm2_5_b FLOAT,
                pm2_5_atm FLOAT,
                pm2_5_atm_a FLOAT,
                pm2_5_atm_b FLOAT,
                pm2_5_cf_1 FLOAT,
                pm2_5_cf_1_a FLOAT,
                pm2_5_cf_1_b FLOAT)"""

        # Since we can't have decimals in variable names, we do pm2_5 instead of pm2.5
        create_pm25_pseudo_average_fields = """
            CREATE TABLE IF NOT EXISTS pm25_pseudo_average_fields (
                data_time_stamp TIMESTAMP PRIMARY KEY,
                pm2_5_10minute FLOAT,
                pm2_5_10minute_a FLOAT,
                pm2_5_10minute_b FLOAT,
                pm2_5_30minute FLOAT,
                pm2_5_30minute_a FLOAT,
                pm2_5_30minute_b FLOAT,
                pm2_5_60minute FLOAT,
                pm2_5_60minute_a FLOAT,
                pm2_5_60minute_b FLOAT,
                pm2_5_6hour FLOAT,
                pm2_5_6hour_a FLOAT,
                pm2_5_6hour_b FLOAT,
                pm2_5_24hour FLOAT,
                pm2_5_24hour_a FLOAT,
                pm2_5_24hour_b FLOAT,
                pm2_5_1week FLOAT,
                pm2_5_1week_a FLOAT,
                pm2_5_1week_b FLOAT)"""

        # Since we can't have decimals in variable names, we do pm10_0 instead of pm10.0
        create_pm100_fields = """
            CREATE TABLE IF NOT EXISTS pm100_fields (
                data_time_stamp TIMESTAMP PRIMARY KEY,
                pm10_0 FLOAT,
                pm10_0_a FLOAT,
                pm10_0_b FLOAT,
                pm10_0_atm FLOAT,
                pm10_0_atm_a FLOAT,
                pm10_0_atm_b FLOAT,
                pm10_0_cf_1 FLOAT,
                pm10_0_cf_1_a FLOAT,
                pm10_0_cf_1_b FLOAT)"""

        # Note we can not start column names with numbers. So 0_3_um_count becomes um_count_0_3
        create_particle_count_fields = """
            CREATE TABLE IF NOT EXISTS particle_count_fields (
                data_time_stamp TIMESTAMP PRIMARY KEY,
                um_count_0_3 FLOAT,
                um_count_a_0_3 FLOAT,
                um_count_b_0_3 FLOAT,
                um_count_0_5 FLOAT,
                um_count_a_0_5 FLOAT,
                um_count_b_0_5 FLOAT,
                um_count_1_0 FLOAT,
                um_count_a_1_0 FLOAT,
                um_count_b_1_0 FLOAT,
                um_count_2_5 FLOAT,
                um_count_a_2_5 FLOAT,
                um_count_b_2_5 FLOAT,
                um_count_5_0 FLOAT,
                um_count_a_5_0 FLOAT,
                um_count_b_5_0 FLOAT,
                um_count_10_0 FLOAT,
                um_count_a_10_0 FLOAT,
                um_count_b_10_0 FLOAT)"""

        # NOTE TO SELF MAY END UP GETTING RID OF THIS TABLE. I SEE NO USE FOR IT.
        create_thingspeak_fields = """
            CREATE TABLE IF NOT EXISTS thingspeak_fields (
                data_time_stamp TIMESTAMP PRIMARY KEY,
                primary_id_a INT,
                primary_key_a TEXT,
                secondary_id_a INT,
                secondary_key_a TEXT,
                primary_id_b INT,
                primary_key_b TEXT,
                secondary_id_b INT,
                secondary_key_b TEXT)"""

        self.__db_conn.run(create_station_information_and_status_fields_table)
        self.__db_conn.run(create_evironmental_fields_table)
        self.__db_conn.run(create_miscellaneous_fields)
        self.__db_conn.run(create_pm10_fields)
        self.__db_conn.run(create_pm25_fields)
        self.__db_conn.run(create_pm25_pseudo_average_fields)
        self.__db_conn.run(create_pm100_fields)
        self.__db_conn.run(create_particle_count_fields)
        self.__db_conn.run(create_thingspeak_fields)

    def __convert_psql_tables_to_hyper_tables(self):
        """
            A method to convert our PSQL tables to TimeScaleDB hyper tables.
        """

        self.__db_conn.run(
            """SELECT create_hypertable('station_information_and_status_fields', 'data_time_stamp')""")
        self.__db_conn.run(
            """SELECT create_hypertable('evironmental_fields', 'data_time_stamp')""")
        self.__db_conn.run(
            """SELECT create_hypertable('miscellaneous_fields', 'data_time_stamp')""")
        self.__db_conn.run(
            """SELECT create_hypertable('pm10_fields', 'data_time_stamp')""")
        self.__db_conn.run(
            """SELECT create_hypertable('pm25_fields', 'data_time_stamp')""")
        self.__db_conn.run(
            """SELECT create_hypertable('pm25_pseudo_average_fields', 'data_time_stamp')""")
        self.__db_conn.run(
            """SELECT create_hypertable('pm100_fields', 'data_time_stamp')""")
        self.__db_conn.run(
            """SELECT create_hypertable('particle_count_fields', 'data_time_stamp')""")
        self.__db_conn.run(
            """SELECT create_hypertable('thingspeak_fields', 'data_time_stamp')""")

    def get_sensor_data(self, sensor_index, read_key=None, fields=None):
        """
            Request data from a single sensor.
            :param int sensor_index: A valid PurpleAirAPI sensor index.
            :param str read_key: A valid PurpleAirAPI private read key.
            :param str fields: A comma delmited string of valid field names.
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

        # As of 07/23/2022 we have 9 tables to insert data into.
        psql_insert_statement_station_information_and_status_fields = """
            INSERT INTO station_information_and_status_fields
                (
                data_time_stamp,
                name,
                icon,
                model,
                hardware,
                location_type,
                private,
                latitude,
                longitude,
                altitude,
                position_rating,
                led_brightness,
                firmware_version,
                firmware_upgrade,
                rssi,
                uptime,
                pa_latency,
                memory,
                last_seen,
                last_modified,
                date_created,
                channel_state,
                channel_flags,
                channel_flags_manual,
                channel_flags_auto,
                confidence,
                confidence_manual,
                confidence_auto
                )
                VALUES 
                (
                CAST(:data_time_stamp AS TIMESTAMP,
                CAST(:name AS TEXT),
                CAST(:icon AS INT),
                CAST(:model AS TEXT),
                CAST(:hardware AS TEXT),
                CAST(:location_type AS INT),
                CAST(:private AS INT),
                CAST(:latitude AS FLOAT),
                CAST(:longitude AS FLOAT),
                CAST(:altitude AS FLOAT),
                CAST(:position_rating AS INT),
                CAST(:led_brightness AS INT),
                CAST(:firmware_version AS TEXT),
                CAST(:firmware_upgrade AS TEXT),
                CAST(:rssi AS INT),
                CAST(:uptime AS INT),
                CAST(:pa_latency AS INT),
                CAST(:memory AS INT),
                CAST(:last_seen AS TIMESTAMP),
                CAST(:last_modified AS TIMESTAMP),
                CAST(:date_created AS TIMESTAMP),
                CAST(:channel_state AS INT),
                CAST(:channel_flags AS INT),
                CAST(:channel_flags_manual AS INT),
                CAST(:channel_flags_auto AS INT),
                CAST(:confidence AS INT),
                CAST(:confidence_manual AS INT),
                CAST(:confidence_auto AS INT)
                )"""

        psql_insert_statement_evironmental_fields = """
            INSERT INTO evironmental_fields
                (
                data_time_stamp,
                humidity,
                humidity_a,
                humidity_b,
                temperature,
                temperature_a,
                temperature_b,
                pressure,
                pressure_a,
                pressure_b) 
                VALUES
                (
                CAST(:data_time_stamp AS TIMESTAMP),
                CAST(:humidity AS INT),
                CAST(:humidity_a AS INT),
                CAST(:humidity_b AS INT),
                CAST(:temperature AS INT),
                CAST(:temperature_a AS INT),
                CAST(:temperature_b AS INT),
                CAST(:pressure AS FLOAT),
                CAST(:pressure_a AS FLOAT),
                CAST(:pressure_b AS FLOAT)
                )"""
        psql_insert_statement_miscellaneous_fields = """INSERT INTO () VALUES ()"""
        psql_insert_statement_pm10_fields = """INSERT INTO () VALUES ()"""
        psql_insert_statement_pm25_fields = """INSERT INTO () VALUES ()"""
        psql_insert_statement_pm25_pseudo_average_fields = """INSERT INTO () VALUES ()"""
        psql_insert_statement_pm100_fields = """INSERT INTO () VALUES ()"""
        psql_insert_statement_particle_count_fields = """INSERT INTO () VALUES ()"""
        psql_insert_statement_thingspeak_fields = """INSERT INTO () VALUES ()"""

    def get_multiple_sensors_data(self):
        """
            Request data from a multiple sensors.
        """
        pass

    def store_multiple_sensors_data(self):
        """
            Insert the multiple sensors data into the database.
        """
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Collect data from PurpleAir sensors and insert into a database!")
    parser.add_argument("-db_usr",  required=True, dest="db_usr",
                        type=str, help="The PSQL database user")
    parser.add_argument("-db_host", required=False, default="localhost",
                        dest="db_host", type=str, help="The PSQL database host")
    parser.add_argument("-db", required=True, dest="db",
                        type=str, help="The PSQL database name")
    parser.add_argument("-db_port", required=False, default=5432,
                        dest="db_port", type=str, help="The PSQL database port number")
    parser.add_argument("-db_pwd",  required=False, default=None,
                        dest="db_pwd", type=str, help="The PSQL database password")
    parser.add_argument("-paa_read_key",  required=True,
                        dest="paa_read_key", type=str, help="The PurpleAirAPI Read key")
    parser.add_argument("-paa_sensor_index",  required=True,
                        dest="paa_sensor_index", type=int, help="The PurpleAirAPI sensor index")

    args = parser.parse_args()

    # Make the PSQL DB connection with CML args
    the_psql_db_conn = pg8000.connect(
        user=args.db_usr,
        host=args.db_host,
        database=args.db,
        port=args.db_port,
        password=args.db_pwd)

    # Make an instance our our data logger
    the_paa_data_logger = PurpleAirDataLogger(
        args.paa_read_key, the_psql_db_conn)

    while True:
        # We will request data once every 65 seconds.
        print("Requesting new data...")
        sensor_data = the_paa_data_logger.get_sensor_data(
            args.paa_sensor_index)
        print("Waiting 65 seconds before requesting new data again...")
        sleep(65)
