#!/usr/bin/env python3

"""
    Copyright 2022 carlkid1499, All rights reserved.
    A file containing PSQL statements defined as constants.
    Generate the PSQL query strings. For simplicity our table names will match
    what the PurpleAir documentation says. We will do the same for table column names.
"""

#: PSQL statement for station_information_and_status_fields table
CREATE_STATION_INFORMATION_AND_STATUS_FIELDS_TABLE = """
    CREATE TABLE IF NOT EXISTS station_information_and_status_fields (
        data_time_stamp TIMESTAMPTZ NOT NULL,
        sensor_index INT NOT NULL,
        name TEXT NULL,
        icon INT NULL,
        model TEXT NULL,
        hardware TEXT NULL,
        location_type INT NULL,
        private INT NULL,
        latitude FLOAT NULL,
        longitude FLOAT NULL,
        altitude FLOAT NULL,
        position_rating INT NULL,
        led_brightness INT NULL,
        firmware_version TEXT NULL,
        firmware_upgrade TEXT NULL,
        rssi INT NULL,
        uptime INT NULL,
        pa_latency INT NULL,
        memory INT NULL,
        last_seen TIMESTAMPTZ NULL,
        last_modified TIMESTAMPTZ NULL,
        date_created TIMESTAMPTZ NULL,
        channel_state INT NULL,
        channel_flags INT NULL,
        channel_flags_manual INT NULL,
        channel_flags_auto INT NULL,
        confidence INT NULL,
        confidence_manual INT NULL,
        confidence_auto INT NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: PSQL statement for environmental_fields table
CREATE_ENVIRONMENTAL_FIELDS_TABLE = """
    CREATE TABLE IF NOT EXISTS environmental_fields (
        data_time_stamp TIMESTAMPTZ NOT NULL,
        sensor_index INT NOT NULL,
        humidity INT NULL,
        humidity_a INT NULL,
        humidity_b INT NULL,
        temperature INT NULL,
        temperature_a INT NULL,
        temperature_b INT NULL,
        pressure FLOAT NULL,
        pressure_a FLOAT NULL,
        pressure_b FLOAT NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: PSQL statement for miscellaneous_fields table
CREATE_MISCELLANEOUS_FIELDS = """
    CREATE TABLE IF NOT EXISTS miscellaneous_fields (
        data_time_stamp TIMESTAMPTZ NOT NULL,
        sensor_index INT NOT NULL,
        voc FLOAT NULL,
        voc_a FLOAT NULL,
        voc_b FLOAT NULL,
        ozone1 FLOAT NULL,
        analog_input FLOAT NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note: Since we can't have decimals in variable names, we do pm1_0 instead of pm1.0
#: PSQL statement for pm1_0_fields table
CREATE_PM1_0_FIELDS = """
    CREATE TABLE IF NOT EXISTS pm1_0_fields(
        data_time_stamp TIMESTAMPTZ NOT NULL,
        sensor_index INT NOT NULL,
        pm1_0 FLOAT NULL,
        pm1_0_a FLOAT NULL,
        pm1_0_b FLOAT NULL,
        pm1_0_atm FLOAT NULL,
        pm1_0_atm_a FLOAT NULL,
        pm1_0_atm_b FLOAT NULL,
        pm1_0_cf_1 FLOAT NULL,
        pm1_0_cf_1_a FLOAT NULL,
        pm1_0_cf_1_b FLOAT NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note: Since we can't have decimals in variable names, we do pm2_5 instead of pm2.5
#: PSQL statement for pm2_5_fields table
CREATE_PM2_5_FIELDS = """
    CREATE TABLE IF NOT EXISTS pm2_5_fields (
        data_time_stamp TIMESTAMPTZ NOT NULL,
        sensor_index INT NOT NULL,
        pm2_5_alt FLOAT NULL,
        pm2_5_alt_a FLOAT NULL,
        pm2_5_alt_b FLOAT NULL,
        pm2_5 FLOAT NULL,
        pm2_5_a FLOAT NULL,
        pm2_5_b FLOAT NULL,
        pm2_5_atm FLOAT NULL,
        pm2_5_atm_a FLOAT NULL,
        pm2_5_atm_b FLOAT NULL,
        pm2_5_cf_1 FLOAT NULL,
        pm2_5_cf_1_a FLOAT NULL,
        pm2_5_cf_1_b FLOAT NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note: Since we can't have decimals in variable names, we do pm2_5 instead of pm2.5
#: PSQL statement for pm2_5_pseudo_average_fields table
CREATE_PM2_5_PSEUDO_AVERAGE_FIELDS = """
    CREATE TABLE IF NOT EXISTS pm2_5_pseudo_average_fields (
        data_time_stamp TIMESTAMPTZ NOT NULL,
        sensor_index INT NOT NULL,
        pm2_5_10minute FLOAT NULL,
        pm2_5_10minute_a FLOAT NULL,
        pm2_5_10minute_b FLOAT NULL,
        pm2_5_30minute FLOAT NULL,
        pm2_5_30minute_a FLOAT NULL,
        pm2_5_30minute_b FLOAT NULL,
        pm2_5_60minute FLOAT NULL,
        pm2_5_60minute_a FLOAT NULL,
        pm2_5_60minute_b FLOAT NULL,
        pm2_5_6hour FLOAT NULL,
        pm2_5_6hour_a FLOAT NULL,
        pm2_5_6hour_b FLOAT NULL,
        pm2_5_24hour FLOAT NULL,
        pm2_5_24hour_a FLOAT NULL,
        pm2_5_24hour_b FLOAT NULL,
        pm2_5_1week FLOAT NULL,
        pm2_5_1week_a FLOAT NULL,
        pm2_5_1week_b FLOAT NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note: Since we can't have decimals in variable names, we do pm10_0 instead of pm10.0
#: PSQL statement for pm10_0_fields table
CREATE_PM10_0_FIELDS = """
    CREATE TABLE IF NOT EXISTS pm10_0_fields (
        data_time_stamp TIMESTAMPTZ NOT NULL,
        sensor_index INT NOT NULL,
        pm10_0 FLOAT NULL,
        pm10_0_a FLOAT NULL,
        pm10_0_b FLOAT NULL,
        pm10_0_atm FLOAT NULL,
        pm10_0_atm_a FLOAT NULL,
        pm10_0_atm_b FLOAT NULL,
        pm10_0_cf_1 FLOAT NULL,
        pm10_0_cf_1_a FLOAT NULL,
        pm10_0_cf_1_b FLOAT NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note: we can not start column names with numbers. So 0_3_um_count becomes um_count_0_3
#: PSQL statement for particle_count_fields table
CREATE_PARTICLE_COUNT_FIELDS = """
    CREATE TABLE IF NOT EXISTS particle_count_fields (
        data_time_stamp TIMESTAMPTZ NOT NULL,
        sensor_index INT NOT NULL,
        um_count_0_3 FLOAT NULL,
        um_count_a_0_3 FLOAT NULL,
        um_count_b_0_3 FLOAT NULL,
        um_count_0_5 FLOAT NULL,
        um_count_a_0_5 FLOAT NULL,
        um_count_b_0_5 FLOAT NULL,
        um_count_1_0 FLOAT NULL,
        um_count_a_1_0 FLOAT NULL,
        um_count_b_1_0 FLOAT NULL,
        um_count_2_5 FLOAT NULL,
        um_count_a_2_5 FLOAT NULL,
        um_count_b_2_5 FLOAT NULL,
        um_count_5_0 FLOAT NULL,
        um_count_a_5_0 FLOAT NULL,
        um_count_b_5_0 FLOAT NULL,
        um_count_10_0 FLOAT NULL,
        um_count_a_10_0 FLOAT NULL,
        um_count_b_10_0 FLOAT NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note TO SELF MAY END UP GETTING RID OF THIS TABLE. I SEE NO USE FOR IT.
#: PSQL statement for thingspeak_fields table
CREATE_THINGSPEAK_FIELDS = """
    CREATE TABLE IF NOT EXISTS thingspeak_fields (
        data_time_stamp TIMESTAMPTZ NOT NULL,
        sensor_index INT NOT NULL,
        primary_id_a INT NULL,
        primary_key_a TEXT NULL,
        secondary_id_a INT NULL,
        secondary_key_a TEXT NULL,
        primary_id_b INT NULL,
        primary_key_b TEXT NULL,
        secondary_id_b INT NULL,
        secondary_key_b TEXT NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

# As of 07/23/2022 we have 9 tables to insert data into.
#: PSQL insert statement for station_information_and_status_fields
PSQL_INSERT_STATEMENT_STATION_INFORMATION_AND_STATUS_FIELDS = """
    INSERT INTO station_information_and_status_fields
        (
            data_time_stamp,
            sensor_index,
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
            CAST(:data_time_stamp AS TIMESTAMPTZ),
            CAST(:sensor_index AS INT),
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
            CAST(:last_seen AS TIMESTAMPTZ),
            CAST(:last_modified AS TIMESTAMPTZ),
            CAST(:date_created AS TIMESTAMPTZ),
            CAST(:channel_state AS INT),
            CAST(:channel_flags AS INT),
            CAST(:channel_flags_manual AS INT),
            CAST(:channel_flags_auto AS INT),
            CAST(:confidence AS INT),
            CAST(:confidence_manual AS INT),
            CAST(:confidence_auto AS INT)
        )"""

#: PSQL insert statement for environmental_fields
PSQL_INSERT_STATEMENT_ENVIRONMENTAL_FIELDS = """
    INSERT INTO environmental_fields
        (
            data_time_stamp,
            sensor_index,
            humidity,
            humidity_a,
            humidity_b,
            temperature,
            temperature_a,
            temperature_b,
            pressure,
            pressure_a,
            pressure_b
        ) 
        VALUES
        (
            CAST(:data_time_stamp AS TIMESTAMPTZ),
            CAST(:sensor_index AS INT),
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

#: PSQL insert statement for miscellaneous_fields
PSQL_INSERT_STATEMENT_MISCELLANEOUS_FIELDS = """
    INSERT INTO miscellaneous_fields
        (
            data_time_stamp,
            sensor_index,
            voc,
            voc_a,
            voc_b,
            ozone1,
            analog_input
        ) 
        VALUES
        (
            CAST(:data_time_stamp AS TIMESTAMPTZ),
            CAST(:sensor_index AS INT),
            CAST(:voc AS FLOAT),
            CAST(:voc_a AS FLOAT),
            CAST(:voc_b AS FLOAT),
            CAST(:ozone1 AS FLOAT),
            CAST(:analog_input AS FLOAT)
        )"""

#: PSQL insert statement for pm1_0_fields
PSQL_INSERT_STATEMENT_PM1_0_FIELDS = """
    INSERT INTO pm1_0_fields
        (
            data_time_stamp,
            sensor_index,
            pm1_0,
            pm1_0_a,
            pm1_0_b,
            pm1_0_atm,
            pm1_0_atm_a,
            pm1_0_atm_b,
            pm1_0_cf_1,
            pm1_0_cf_1_a,
            pm1_0_cf_1_b
        )
        VALUES
        (
            CAST(:data_time_stamp AS TIMESTAMPTZ),
            CAST(:sensor_index AS INT),
            CAST(:pm1_0 AS FLOAT),
            CAST(:pm1_0_a AS FLOAT),
            CAST(:pm1_0_b AS FLOAT),
            CAST(:pm1_0_atm AS FLOAT),
            CAST(:pm1_0_atm_a AS FLOAT),
            CAST(:pm1_0_atm_b AS FLOAT),
            CAST(:pm1_0_cf_1 AS FLOAT),
            CAST(:pm1_0_cf_1_a AS FLOAT),
            CAST(:pm1_0_cf_1_b AS FLOAT)
        )"""

#: PSQL insert statement for pm2_5_fields
PSQL_INSERT_STATEMENT_PM2_5_FIELDS = """
    INSERT INTO pm2_5_fields
        (
            data_time_stamp,
            sensor_index,
            pm2_5_alt,
            pm2_5_alt_a,
            pm2_5_alt_b,
            pm2_5,
            pm2_5_a,
            pm2_5_b,
            pm2_5_atm,
            pm2_5_atm_a,
            pm2_5_atm_b,
            pm2_5_cf_1,
            pm2_5_cf_1_a,
            pm2_5_cf_1_b
        ) 
        VALUES
        (
            CAST(:data_time_stamp AS TIMESTAMPTZ),
            CAST(:sensor_index AS INT),
            CAST(:pm2_5_alt AS FLOAT),
            CAST(:pm2_5_alt_a AS FLOAT),
            CAST(:pm2_5_alt_b AS FLOAT),
            CAST(:pm2_5 AS FLOAT),
            CAST(:pm2_5_a AS FLOAT),
            CAST(:pm2_5_b AS FLOAT),
            CAST(:pm2_5_atm AS FLOAT),
            CAST(:pm2_5_atm_a AS FLOAT),
            CAST(:pm2_5_atm_b AS FLOAT),
            CAST(:pm2_5_cf_1 AS FLOAT),
            CAST(:pm2_5_cf_1_a AS FLOAT),
            CAST(:pm2_5_cf_1_b AS FLOAT)
        )"""

#: PSQL insert statement for pm2_5_pseudo_average_fields
PSQL_INSERT_STATEMENT_PM2_5_PSEUDO_AVERAGE_FIELDS = """
    INSERT INTO pm2_5_pseudo_average_fields 
    (
        data_time_stamp,
        sensor_index,
        pm2_5_10minute,
        pm2_5_10minute_a,
        pm2_5_10minute_b,
        pm2_5_30minute,
        pm2_5_30minute_a,
        pm2_5_30minute_b,
        pm2_5_60minute,
        pm2_5_60minute_a,
        pm2_5_60minute_b,
        pm2_5_6hour,
        pm2_5_6hour_a,
        pm2_5_6hour_b,
        pm2_5_24hour,
        pm2_5_24hour_a,
        pm2_5_24hour_b,
        pm2_5_1week,
        pm2_5_1week_a,
        pm2_5_1week_b
    )
    VALUES
    (
        CAST(:data_time_stamp AS TIMESTAMPTZ),
        CAST(:sensor_index AS INT),
        CAST(:pm2_5_10minute AS FLOAT),
        CAST(:pm2_5_10minute_a AS FLOAT),
        CAST(:pm2_5_10minute_b AS FLOAT),
        CAST(:pm2_5_30minute AS FLOAT),
        CAST(:pm2_5_30minute_a AS FLOAT),
        CAST(:pm2_5_30minute_b AS FLOAT),
        CAST(:pm2_5_60minute AS FLOAT),
        CAST(:pm2_5_60minute_a AS FLOAT),
        CAST(:pm2_5_60minute_b AS FLOAT),
        CAST(:pm2_5_6hour AS FLOAT),
        CAST(:pm2_5_6hour_a AS FLOAT),
        CAST(:pm2_5_6hour_b AS FLOAT),
        CAST(:pm2_5_24hour AS FLOAT),
        CAST(:pm2_5_24hour_a AS FLOAT),
        CAST(:pm2_5_24hour_b AS FLOAT),
        CAST(:pm2_5_1week AS FLOAT),
        CAST(:pm2_5_1week_a AS FLOAT),
        CAST(:pm2_5_1week_b AS FLOAT)
    )"""

#: PSQL insert statement for pm10_0_fields
PSQL_INSERT_STATEMENT_PM10_0_FIELDS = """
    INSERT INTO pm10_0_fields
    (
        data_time_stamp,
        sensor_index,
        pm10_0,
        pm10_0_a,
        pm10_0_b,
        pm10_0_atm,
        pm10_0_atm_a,
        pm10_0_atm_b,
        pm10_0_cf_1,
        pm10_0_cf_1_a,
        pm10_0_cf_1_b
    ) 
    VALUES
    (
        CAST(:data_time_stamp AS TIMESTAMPTZ),
        CAST(:sensor_index AS INT),
        CAST(:pm10_0 AS FLOAT),
        CAST(:pm10_0_a AS FLOAT),
        CAST(:pm10_0_b AS FLOAT),
        CAST(:pm10_0_atm AS FLOAT),
        CAST(:pm10_0_atm_a AS FLOAT),
        CAST(:pm10_0_atm_b AS FLOAT),
        CAST(:pm10_0_cf_1 AS FLOAT),
        CAST(:pm10_0_cf_1_a AS FLOAT),
        CAST(:pm10_0_cf_1_b AS FLOAT)
    )"""

#: PSQL insert statement for particle_count_fields
PSQL_INSERT_STATEMENT_PARTICLE_COUNT_FIELDS = """
    INSERT INTO particle_count_fields 
    (
        data_time_stamp,
        sensor_index,
        um_count_0_3,
        um_count_a_0_3,
        um_count_b_0_3,
        um_count_0_5,
        um_count_a_0_5,
        um_count_b_0_5,
        um_count_1_0,
        um_count_a_1_0,
        um_count_b_1_0,
        um_count_2_5,
        um_count_a_2_5,
        um_count_b_2_5,
        um_count_5_0,
        um_count_a_5_0,
        um_count_b_5_0,
        um_count_10_0,
        um_count_a_10_0,
        um_count_b_10_0
    )
    VALUES
    (
        CAST(:data_time_stamp AS TIMESTAMPTZ),
        CAST(:sensor_index AS INT),
        CAST(:um_count_0_3 AS FLOAT),
        CAST(:um_count_a_0_3 AS FLOAT),
        CAST(:um_count_b_0_3 AS FLOAT),
        CAST(:um_count_0_5 AS FLOAT),
        CAST(:um_count_a_0_5 AS FLOAT),
        CAST(:um_count_b_0_5 AS FLOAT),
        CAST(:um_count_1_0 AS FLOAT),
        CAST(:um_count_a_1_0 AS FLOAT),
        CAST(:um_count_b_1_0 AS FLOAT),
        CAST(:um_count_2_5 AS FLOAT),
        CAST(:um_count_a_2_5 AS FLOAT),
        CAST(:um_count_b_2_5 AS FLOAT),
        CAST(:um_count_5_0 AS FLOAT),
        CAST(:um_count_a_5_0 AS FLOAT),
        CAST(:um_count_b_5_0 AS FLOAT),
        CAST(:um_count_10_0 AS FLOAT),
        CAST(:um_count_a_10_0 AS FLOAT),
        CAST(:um_count_b_10_0 AS FLOAT)
    )"""

#: PSQL insert statement for thingspeak_fields
PSQL_INSERT_STATEMENT_THINGSPEAK_FIELDS = """
    INSERT INTO thingspeak_fields
    (
        data_time_stamp,
        sensor_index,
        primary_id_a,
        primary_key_a,
        secondary_id_a,
        secondary_key_a,
        primary_id_b,
        primary_key_b,
        secondary_id_b,
        secondary_key_b
    )
    VALUES
    (
        CAST(:data_time_stamp AS TIMESTAMPTZ),
        CAST(:sensor_index AS INT),
        CAST(:primary_id_a AS INT),
        CAST(:primary_key_a AS TEXT),
        CAST(:secondary_id_a AS INT),
        CAST(:secondary_key_a AS TEXT),
        CAST(:primary_id_b AS INT),
        CAST(:primary_key_b AS TEXT),
        CAST(:secondary_id_b AS INT),
        CAST(:secondary_key_b AS TEXT)
    )"""

#: PSQL statement to drop all tables in the database
PSQL_DROP_ALL_TABLES = """
    DROP TABLE station_information_and_status_fields;
    DROP TABLE environmental_fields;
    DROP TABLE miscellaneous_fields;
    DROP TABLE pm1_0_fields;
    DROP TABLE pm2_5_fields;
    DROP TABLE pm2_5_pseudo_average_fields;
    DROP TABLE pm10_0_fields;
    DROP TABLE particle_count_fields;
    DROP TABLE thingspeak_fields;
    """

#: PSQL statement to see active TimescaleDB compression policies
#: Documentation can be found here: https://docs.timescale.com/timescaledb/latest/how-to-guides/compression/about-compression/
PSQL_GET_LIST_OF_ACTIVE_COMPRESSION_POLICIES = """
    SELECT hypertable_name FROM timescaledb_information.jobs
    WHERE proc_name='policy_compression';
    """

#: PSQL statement to create a TimescaleDB Materialized View
#: Documentation can be found here: https://docs.timescale.com/api/latest/continuous-aggregates/create_materialized_view/
PSQL_CREATE_MATERIALIZED_VIEW_SENSOR_INDEX_AND_NAME_1HOUR_AGGREGATE = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_index_and_name_1hour_aggregate(data_time_stamp, sensor_index, name)
    WITH (timescaledb.continuous) AS
	    SELECT time_bucket('1h', data_time_stamp), sensor_index, name
	    FROM station_information_and_status_fields
	    GROUP BY time_bucket('1h', data_time_stamp), sensor_index, name
    WITH NO DATA;
    """

#: PSQL statement to add a TimescaleDB continuous refresh policy on the sensor_index_and_name_1hour_aggregate materialized view
#: Documentation can be found here: https://docs.timescale.com/timescaledb/latest/how-to-guides/continuous-aggregates/refresh-policies/
PSQL_CREATE_CONTINUOUS_AGGREGATE_POLICY_ON_SENSOR_INDEX_AND_NAME_1HOUR_AGGREGATE = """
    SELECT add_continuous_aggregate_policy('sensor_index_and_name_1hour_aggregate',
    start_offset => INTERVAL '3 h',
    end_offset => INTERVAL '1 h',
    schedule_interval => INTERVAL '1 h',
    if_not_exists => true);
    """

#: PSQL statement to add a TimescaleDB data retention policy on the sensor_index_and_name_1hour_aggregate materialized view
#: Documentation can be found here: https://docs.timescale.com/timescaledb/latest/how-to-guides/data-retention/data-retention-with-continuous-aggregates/
PSQL_CREATE_DATA_RETENTION_POLICY_ON_SENSOR_INDEX_AND_NAME_1HOUR_AGGREGATE = """
    SELECT add_retention_policy('sensor_index_and_name_1hour_aggregate',
    INTERVAL '8 hours',
    if_not_exists => true); 
    """
