#!/usr/bin/env python3

"""
    A python class designed to use the PurpleAirAPI for sensor data.
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

    def __create_psql_db(self):
        """
            Create the PSQL database if it doesn't exist already
        """
        pass

    def get_sensor_data(self):
        """
            Request data from a single sensor.
        """
        pass

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
    #the_paa_data_logger = PurpleAirDataLogger(args.paa_read_key, the_psql_db_conn)

    # For best practice from PurpleAir:
    # "The data from individual sensors will update no less than every 30 seconds.
    # As a courtesy, we ask that you limit the number of requests to no more than
    # once every 1 to 10 minutes, assuming you are only using the API to obtain data
    # from sensors. If retrieving data from multiple sensors at once, please send a
    # single request rather than individual requests in succession."

    while True:
        # We will request data once every 65 seconds.
        print("Requesting new data...")

        print("Waiting 65 seconds before requesting new data again...")
        sleep(65)
