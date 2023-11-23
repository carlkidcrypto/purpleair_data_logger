#!/usr/bin/env python3

"""
    Copyright 2023 carlkidcrypto, All rights reserved.
    A python class designed to use the PurpleAirAPI for requesting sensor(s) data.
    Data will be inserted into a PSQL database.

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


from purpleair_data_logger.PurpleAirPSQLQueryStatements import (
    PSQL_INSERT_STATEMENT_ENVIRONMENTAL_FIELDS,
    PSQL_INSERT_STATEMENT_MISCELLANEOUS_FIELDS,
    PSQL_INSERT_STATEMENT_PARTICLE_COUNT_FIELDS,
    PSQL_INSERT_STATEMENT_PM10_0_FIELDS,
    PSQL_INSERT_STATEMENT_PM1_0_FIELDS,
    PSQL_INSERT_STATEMENT_PM2_5_FIELDS,
    PSQL_INSERT_STATEMENT_PM2_5_PSEUDO_AVERAGE_FIELDS,
    PSQL_INSERT_STATEMENT_STATION_INFORMATION_AND_STATUS_FIELDS,
    PSQL_INSERT_STATEMENT_THINGSPEAK_FIELDS,
    CREATE_PARTICLE_COUNT_FIELDS,
    CREATE_PM10_0_FIELDS,
    CREATE_PM1_0_FIELDS,
    CREATE_PM2_5_FIELDS,
    CREATE_PM2_5_PSEUDO_AVERAGE_FIELDS,
    CREATE_ENVIRONMENTAL_FIELDS_TABLE,
    CREATE_MISCELLANEOUS_FIELDS,
    CREATE_STATION_INFORMATION_AND_STATUS_FIELDS_TABLE,
    CREATE_THINGSPEAK_FIELDS,
    PSQL_DROP_ALL_TABLES,
    PSQL_GET_LIST_OF_ACTIVE_COMPRESSION_POLICIES,
    PSQL_CREATE_MATERIALIZED_VIEW_SENSOR_INDEX_AND_NAME_1HOUR_AGGREGATE,
    PSQL_CREATE_CONTINUOUS_AGGREGATE_POLICY_ON_SENSOR_INDEX_AND_NAME_1HOUR_AGGREGATE,
    PSQL_CREATE_DATA_RETENTION_POLICY_ON_SENSOR_INDEX_AND_NAME_1HOUR_AGGREGATE,
)
import pg8000
from datetime import datetime, timezone
import sys


class PurpleAirPSQLDataLogger(PurpleAirDataLogger):
    """
    The logger class. For now we will ingest data into a TimeScaleDB PostgreSQL
    database. Then we will use Grafana to visualize said data.
    """

    def __init__(self, PurpleAirAPIReadKey, PurpleAirAPIWriteKey, psql_db_conn):
        """
        :param str PurpleAirAPIReadKey: A valid PurpleAirAPI Read key
        :param object psql_db_conn: A valid PG8000 database connection
        """

        # Inherit everything from the parent base class: PurpleAirDataLogger
        super().__init__(PurpleAirAPIReadKey, PurpleAirAPIWriteKey)

        # Make our psql database connection
        self._db_conn = psql_db_conn

        # A list of all acceptable table names
        self._acceptable_table_names_string_list = [
            "station_information_and_status_fields",
            "environmental_fields",
            "miscellaneous_fields",
            "pm1_0_fields",
            "pm2_5_fields",
            "pm2_5_pseudo_average_fields",
            "pm10_0_fields",
            "particle_count_fields",
            "thingspeak_fields",
        ]

        # Make our PSQL Tables
        self._create_psql_db_tables()

        # Convert our PSQL tables to hyper tables
        self._convert_psql_tables_to_hyper_tables()

        # Create compression policies
        self._configure_data_compression_policies()

        # Create continuous aggregates and materialized views
        self._configure_continuous_aggregates()

        # Create some prepared statements
        self._db_prepared_statements = {}
        self._db_prepared_statements[
            "station_information_and_status_fields"
        ] = self._db_conn.prepare(
            PSQL_INSERT_STATEMENT_STATION_INFORMATION_AND_STATUS_FIELDS
        )
        self._db_prepared_statements["environmental_fields"] = self._db_conn.prepare(
            PSQL_INSERT_STATEMENT_ENVIRONMENTAL_FIELDS
        )
        self._db_prepared_statements["miscellaneous_fields"] = self._db_conn.prepare(
            PSQL_INSERT_STATEMENT_MISCELLANEOUS_FIELDS
        )
        self._db_prepared_statements["pm1_0_fields"] = self._db_conn.prepare(
            PSQL_INSERT_STATEMENT_PM1_0_FIELDS
        )
        self._db_prepared_statements["pm2_5_fields"] = self._db_conn.prepare(
            PSQL_INSERT_STATEMENT_PM2_5_FIELDS
        )
        self._db_prepared_statements[
            "pm2_5_pseudo_average_fields"
        ] = self._db_conn.prepare(PSQL_INSERT_STATEMENT_PM2_5_PSEUDO_AVERAGE_FIELDS)
        self._db_prepared_statements["pm10_0_fields"] = self._db_conn.prepare(
            PSQL_INSERT_STATEMENT_PM10_0_FIELDS
        )
        self._db_prepared_statements["particle_count_fields"] = self._db_conn.prepare(
            PSQL_INSERT_STATEMENT_PARTICLE_COUNT_FIELDS
        )
        self._db_prepared_statements["thingspeak_fields"] = self._db_conn.prepare(
            PSQL_INSERT_STATEMENT_THINGSPEAK_FIELDS
        )

        # Commit to the db
        self._db_conn.commit()

    @property
    def get_acceptable_table_names_string_list(self):
        """
        A getter method that will simply return the contents of
        the acceptable_table_names_string_list. This is a list
        of all the tables that this DataLogger uses and knows about.
        """

        return self._acceptable_table_names_string_list

    def _create_psql_db_tables(self):
        """
        Create the PSQL database tables if they don't exist already

        We will create one table for different data groups. Simply following the
        official PurpleAir documentation. Think Station information and status fields,
        Environmental fields, etc. See website for more information.
        https://api.purpleair.com/#api-sensors-get-sensor-data
        """

        self._db_conn.run(CREATE_STATION_INFORMATION_AND_STATUS_FIELDS_TABLE)
        self._db_conn.run(CREATE_ENVIRONMENTAL_FIELDS_TABLE)
        self._db_conn.run(CREATE_MISCELLANEOUS_FIELDS)
        self._db_conn.run(CREATE_PM1_0_FIELDS)
        self._db_conn.run(CREATE_PM2_5_FIELDS)
        self._db_conn.run(CREATE_PM2_5_PSEUDO_AVERAGE_FIELDS)
        self._db_conn.run(CREATE_PM10_0_FIELDS)
        self._db_conn.run(CREATE_PARTICLE_COUNT_FIELDS)
        self._db_conn.run(CREATE_THINGSPEAK_FIELDS)

    def _convert_psql_tables_to_hyper_tables(self):
        """
        A method to convert our PSQL tables to TimeScaleDB hyper tables.
        """

        for table_name in self._acceptable_table_names_string_list:
            self._db_conn.run(
                f"""SELECT create_hypertable('{table_name}', 'data_time_stamp', if_not_exists => TRUE)"""
            )

    def _configure_data_compression_policies(self):
        """
        A method to set TimescaleDB data compression policies. More information
        can be found here: https://docs.timescale.com/api/latest/compression/add_compression_policy/#add-compression-policy
        """

        # Before we do anything let's get a list of all the current active compression policies
        query_result = self._db_conn.run(PSQL_GET_LIST_OF_ACTIVE_COMPRESSION_POLICIES)

        # Convert our tuple query_result into a list
        compression_policy_list = []
        for row in query_result:
            compression_policy_list.append(str(row[0]))

        for table_name in self._acceptable_table_names_string_list:
            if table_name not in compression_policy_list:
                self._db_conn.run(
                    f"""ALTER TABLE {table_name} SET (timescaledb.compress, timescaledb.compress_orderby = 'data_time_stamp',
                        timescaledb.compress_segmentby = 'sensor_index')"""
                )

                self._db_conn.run(
                    f"""SELECT add_compression_policy('{table_name}', INTERVAL '14d', if_not_exists => TRUE)"""
                )

    def _configure_continuous_aggregates(self):
        """
        A method to set TimescaleDB continuous aggregates policies. More information
        can be found here: https://docs.timescale.com/timescaledb/latest/overview/core-concepts/continuous-aggregates/
        """

        self._db_conn.run(
            PSQL_CREATE_MATERIALIZED_VIEW_SENSOR_INDEX_AND_NAME_1HOUR_AGGREGATE
        )
        self._db_conn.run(
            PSQL_CREATE_CONTINUOUS_AGGREGATE_POLICY_ON_SENSOR_INDEX_AND_NAME_1HOUR_AGGREGATE
        )
        self._db_conn.run(
            PSQL_CREATE_DATA_RETENTION_POLICY_ON_SENSOR_INDEX_AND_NAME_1HOUR_AGGREGATE
        )

    def _convert_unix_epoch_timestamp_to_psql_timestamp(self, unix_epoch_timestamp):
        """
        A method to covert a unix epoch timestamp to a psql timestamp.

        :param int unix_epoch_timestamp: A valid unix epoch timestamp

        :return: A valid psql UTC timestamp or None.
        """

        if unix_epoch_timestamp is None:
            return None

        else:
            return str(datetime.fromtimestamp(unix_epoch_timestamp, timezone.utc))

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
        self._db_prepared_statements["station_information_and_status_fields"].run(
            data_time_stamp=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]
            ),
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
            last_seen=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["last_seen"]
            ),
            last_modified=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["last_modified"]
            ),
            date_created=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["date_created"]
            ),
            channel_state=single_sensor_data_dict["channel_state"],
            channel_flags=single_sensor_data_dict["channel_flags"],
            channel_flags_manual=single_sensor_data_dict["channel_flags_manual"],
            channel_flags_auto=single_sensor_data_dict["channel_flags_auto"],
            confidence=single_sensor_data_dict["confidence"],
            confidence_manual=single_sensor_data_dict["confidence_manual"],
            confidence_auto=single_sensor_data_dict["confidence_auto"],
        )

        self._db_prepared_statements["environmental_fields"].run(
            data_time_stamp=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]
            ),
            sensor_index=single_sensor_data_dict["sensor_index"],
            humidity=single_sensor_data_dict["humidity"],
            humidity_a=single_sensor_data_dict["humidity_a"],
            humidity_b=single_sensor_data_dict["humidity_b"],
            temperature=single_sensor_data_dict["temperature"],
            temperature_a=single_sensor_data_dict["temperature_a"],
            temperature_b=single_sensor_data_dict["temperature_b"],
            pressure=single_sensor_data_dict["pressure"],
            pressure_a=single_sensor_data_dict["pressure_a"],
            pressure_b=single_sensor_data_dict["pressure_b"],
        )

        self._db_prepared_statements["miscellaneous_fields"].run(
            data_time_stamp=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]
            ),
            sensor_index=single_sensor_data_dict["sensor_index"],
            voc=single_sensor_data_dict["voc"],
            voc_a=single_sensor_data_dict["voc_a"],
            voc_b=single_sensor_data_dict["voc_b"],
            ozone1=single_sensor_data_dict["ozone1"],
            analog_input=single_sensor_data_dict["analog_input"],
        )

        self._db_prepared_statements["pm1_0_fields"].run(
            data_time_stamp=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]
            ),
            sensor_index=single_sensor_data_dict["sensor_index"],
            pm1_0=single_sensor_data_dict["pm1.0"],
            pm1_0_a=single_sensor_data_dict["pm1.0_a"],
            pm1_0_b=single_sensor_data_dict["pm1.0_b"],
            pm1_0_atm=single_sensor_data_dict["pm1.0_atm"],
            pm1_0_atm_a=single_sensor_data_dict["pm1.0_atm_a"],
            pm1_0_atm_b=single_sensor_data_dict["pm1.0_atm_b"],
            pm1_0_cf_1=single_sensor_data_dict["pm1.0_cf_1"],
            pm1_0_cf_1_a=single_sensor_data_dict["pm1.0_cf_1_a"],
            pm1_0_cf_1_b=single_sensor_data_dict["pm1.0_cf_1_b"],
        )

        self._db_prepared_statements["pm2_5_fields"].run(
            data_time_stamp=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]
            ),
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
            pm2_5_cf_1_b=single_sensor_data_dict["pm2.5_cf_1_b"],
        )

        self._db_prepared_statements["pm2_5_pseudo_average_fields"].run(
            data_time_stamp=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]
            ),
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
            pm2_5_1week_b=single_sensor_data_dict["pm2.5_1week_b"],
        )

        self._db_prepared_statements["pm10_0_fields"].run(
            data_time_stamp=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]
            ),
            sensor_index=single_sensor_data_dict["sensor_index"],
            pm10_0=single_sensor_data_dict["pm10.0"],
            pm10_0_a=single_sensor_data_dict["pm10.0_a"],
            pm10_0_b=single_sensor_data_dict["pm10.0_b"],
            pm10_0_atm=single_sensor_data_dict["pm10.0_atm"],
            pm10_0_atm_a=single_sensor_data_dict["pm10.0_atm_a"],
            pm10_0_atm_b=single_sensor_data_dict["pm10.0_atm_b"],
            pm10_0_cf_1=single_sensor_data_dict["pm10.0_cf_1"],
            pm10_0_cf_1_a=single_sensor_data_dict["pm10.0_cf_1_a"],
            pm10_0_cf_1_b=single_sensor_data_dict["pm10.0_cf_1_b"],
        )

        self._db_prepared_statements["particle_count_fields"].run(
            data_time_stamp=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]
            ),
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
            um_count_b_10_0=single_sensor_data_dict["10.0_um_count_b"],
        )

        self._db_prepared_statements["thingspeak_fields"].run(
            data_time_stamp=self._convert_unix_epoch_timestamp_to_psql_timestamp(
                single_sensor_data_dict["data_time_stamp"]
            ),
            sensor_index=single_sensor_data_dict["sensor_index"],
            primary_id_a=single_sensor_data_dict["primary_id_a"],
            primary_key_a=single_sensor_data_dict["primary_key_a"],
            secondary_id_a=single_sensor_data_dict["secondary_id_a"],
            secondary_key_a=single_sensor_data_dict["secondary_key_a"],
            primary_id_b=single_sensor_data_dict["primary_id_b"],
            primary_key_b=single_sensor_data_dict["primary_key_b"],
            secondary_id_b=single_sensor_data_dict["secondary_id_b"],
            secondary_key_b=single_sensor_data_dict["secondary_key_b"],
        )

        # Commit to the db
        self._db_conn.commit()

        # Delete some stuff
        del single_sensor_data_dict


if __name__ == "__main__":
    parser = generate_common_arg_parser(
        "Collect data from PurpleAir sensors and insert into a database!"
    )

    parser.add_argument(
        "-db_drop_all_tables",
        action="store_true",
        required=False,
        dest="db_drop_all_tables",
        help="""Set this flag if you wish to drop all
                        tables before loading in new data. Useful if a database change has happened.
                        Note: Make sure to provide a db_usr with DROP rights.
                        WARNING: ALL COLLECTED DATA WILL BE LOST!""",
    )
    parser.add_argument(
        "-db_usr",
        required=True,
        dest="db_usr",
        type=str,
        help="""The PSQL database user""",
    )
    parser.add_argument(
        "-db_host",
        required=False,
        default="localhost",
        dest="db_host",
        type=str,
        help="""The PSQL database host""",
    )
    parser.add_argument(
        "-db", required=True, dest="db", type=str, help="""The PSQL database name"""
    )
    parser.add_argument(
        "-db_port",
        required=False,
        default=5432,
        dest="db_port",
        type=str,
        help="""The PSQL database port number""",
    )
    parser.add_argument(
        "-db_pwd",
        required=False,
        default=None,
        dest="db_pwd",
        type=str,
        help="""The PSQL database password""",
    )

    args = parser.parse_args()

    # Place holders that are used later down
    the_json_file = None
    file_obj = None

    # Second make the PSQL DB connection with CML args
    the_psql_db_conn = pg8000.connect(
        user=args.db_usr,
        host=args.db_host,
        database=args.db,
        port=args.db_port,
        password=args.db_pwd,
    )

    # Before doing step three, check if we wish to drop all tables.
    if args.db_drop_all_tables:
        print(
            """Are you sure you wish to continue? This operation will drop all tables from the database!
        ALL COLLECTED DATA WILL BE LOST!"""
        )
        user_input = input("""Type yes or no to continue: """)
        if "no" in str(user_input):
            sys.exit("""Stopping because you didn't want to continue...""")

        elif "yes" in str(user_input):
            the_psql_db_conn.run(PSQL_DROP_ALL_TABLES)
            the_psql_db_conn.commit()
            sys.exit(
                """All database tables have been dropped. Please rerun with a db_usr who only has insert rights provided..."""
            )

    # Third make an instance our our data logger
    the_paa_psql_data_logger = PurpleAirPSQLDataLogger(
        args.paa_read_key, args.paa_write_key, the_psql_db_conn
    )

    # Fourth choose what run method to execute depending on
    # paa_multiple_sensor_request_json_file/paa_single_sensor_request_json_file/paa_group_sensor_request_json_file
    the_paa_psql_data_logger.validate_parameters_and_run(
        args.paa_multiple_sensor_request_json_file,
        args.paa_single_sensor_request_json_file,
        args.paa_group_sensor_request_json_file,
    )
