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
            confidence_auto"""

        create_evironmental_fields_table = """
        CREATE TABLE IF NOT EXISTS evironmental_fields (
            humidity,
            humidity_a,
            humidity_b,
            temperature,
            temperature_a,
            temperature_b,
            pressure,
            pressure_a,
            pressure_b)"""

        create_miscellaneous_fields = """
        CREATE TABLE IF NOT EXISTS miscellaneous_fields (
            voc,
            voc_a,
            voc_b,
            ozone1,
            analog_input)"""

        # Since we can't have decimals in variable names, we do pm10 instead of pm1.0
        create_pm10_fields = """
        CREATE TABLE IF NOT EXISTS pm10_fields(
            pm1.0,
            pm1.0_a,
            pm1.0_b,
            pm1.0_atm,
            pm1.0_atm_a,
            pm1.0_atm_b,
            pm1.0_cf_1,
            pm1.0_cf_1_a,
            pm1.0_cf_1_b)"""

        # Since we can't have decimals in variable names, we do pm25 instead of pm2.5
        create_pm25_fields = """
        CREATE TABLE IF NOT EXISTS pm25_fields (
            pm2.5_alt,
            pm2.5_alt_a,
            pm2.5_alt_b,
            pm2.5,
            pm2.5_a,
            pm2.5_b,
            pm2.5_atm,
            pm2.5_atm_a,
            pm2.5_atm_b,
            pm2.5_cf_1,
            pm2.5_cf_1_a,
            pm2.5_cf_1_b)"""

        # Since we can't have decimals in variable names, we do pm25 instead of pm2.5
        create_pm25_pseudo_average_fields = """
        CREATE TABLE IF NOT EXISTS pm25_pseudo_average_fields (
            pm2.5_10minute,
            pm2.5_10minute_a,
            pm2.5_10minute_b,
            pm2.5_30minute,
            pm2.5_30minute_a,
            pm2.5_30minute_b,
            pm2.5_60minute,
            pm2.5_60minute_a,
            pm2.5_60minute_b,
            pm2.5_6hour,
            pm2.5_6hour_a,
            pm2.5_6hour_b,
            pm2.5_24hour,
            pm2.5_24hour_a,
            pm2.5_24hour_b,
            pm2.5_1week,
            pm2.5_1week_a,
            pm2.5_1week_b)"""

        # Since we can't have decimals in variable names, we do pm100 instead of pm10.0
        create_pm100_fields = """
        CREATE TABLE IF NOT EXISTS pm100_fields (
            pm10.0,
            pm10.0_a,
            pm10.0_b,
            pm10.0_atm,
            pm10.0_atm_a,
            pm10.0_atm_b,
            pm10.0_cf_1,
            pm10.0_cf_1_a,
            pm10.0_cf_1_b)"""

        create_particle_count_fields = """
        CREATE TABLE IF NOT EXISTS particle_count_fields (
            0.3_um_count,
            0.3_um_count_a,
            0.3_um_count_b,
            0.5_um_count,
            0.5_um_count_a,
            0.5_um_count_b,
            1.0_um_count,
            1.0_um_count_a,
            1.0_um_count_b,
            2.5_um_count,
            2.5_um_count_a,
            2.5_um_count_b,
            5.0_um_count,
            5.0_um_count_a,
            5.0_um_count_b,
            10.0_um_count,
            10.0_um_count_a,
            10.0_um_count_b)"""

        # NOTE TO SELF MAY END OF GETTING RID OF THIS TABLE. I SEE NO USE FOR IT.
        create_thingspeak_fields = """
        CREATE TABLE IF NOT EXISTS thingspeak_fields (
            primary_id_a,
            primary_key_a,
            secondary_id_a,
            secondary_key_a,
            primary_id_b,
            primary_key_b,
            secondary_id_b,
            secondary_key_b)"""

    def get_sensor_data(self, sensor_index, read_key=None, fields=None):
        """
            Request data from a single sensor.
        """

        return self.__paa_obj.request_sensor_data(sensor_index, read_key, fields)

    def store_sensor_data(self):
        """
            Insert the sensor data into the database.
        """
        pass

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
    parser = argparse.ArgumentParser(description="Process some integers.")
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

    args = parser.parse_args()

    #the_psql_db_conn = pg8000.connect()
    the_paa_data_logger = PurpleAirDataLogger(args.paa_read_key, None)

    while True:
        # We will request data once every 65 seconds.
        print("Requesting new data...")

        # For now a random sensor in Greenland
        sensor_data = the_paa_data_logger.get_sensor_data(14867)
        print("Waiting 65 seconds before requesting new data again...")
        sleep(65)
