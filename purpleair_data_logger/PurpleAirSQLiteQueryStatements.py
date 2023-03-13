#!/usr/bin/env python3

"""
    Copyright 2022 carlkidcrypto, All rights reserved.
    A file containing SQLITE statements defined as constants.
    Generate the SQLITE query strings. For simplicity our table names will match
    what the PurpleAir documentation says. We will do the same for table column names.
"""

#: SQLITE statement for station_information_and_status_fields table
CREATE_STATION_INFORMATION_AND_STATUS_FIELDS_TABLE = """
    CREATE TABLE IF NOT EXISTS station_information_and_status_fields (
        data_time_stamp TEXT NOT NULL,
        sensor_index INTEGER NOT NULL,
        name TEXT NULL,
        icon INTEGER NULL,
        model TEXT NULL,
        hardware TEXT NULL,
        location_type INTEGER NULL,
        private INTEGER NULL,
        latitude REAL NULL,
        longitude REAL NULL,
        altitude REAL NULL,
        position_rating INTEGER NULL,
        led_brightness INTEGER NULL,
        firmware_version TEXT NULL,
        firmware_upgrade TEXT NULL,
        rssi INTEGER NULL,
        uptime INTEGER NULL,
        pa_latency INTEGER NULL,
        memory INTEGER NULL,
        last_seen TEXT NULL,
        last_modified TEXT NULL,
        date_created TEXT NULL,
        channel_state INTEGER NULL,
        channel_flags INTEGER NULL,
        channel_flags_manual INTEGER NULL,
        channel_flags_auto INTEGER NULL,
        confidence INTEGER NULL,
        confidence_manual INTEGER NULL,
        confidence_auto INTEGER NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: SQLITE statement for environmental_fields table
CREATE_ENVIRONMENTAL_FIELDS_TABLE = """
    CREATE TABLE IF NOT EXISTS environmental_fields (
        data_time_stamp TEXT NOT NULL,
        sensor_index INTEGER NOT NULL,
        humidity INTEGER NULL,
        humidity_a INTEGER NULL,
        humidity_b INTEGER NULL,
        temperature INTEGER NULL,
        temperature_a INTEGER NULL,
        temperature_b INTEGER NULL,
        pressure REAL NULL,
        pressure_a REAL NULL,
        pressure_b REAL NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: SQLITE statement for miscellaneous_fields table
CREATE_MISCELLANEOUS_FIELDS = """
    CREATE TABLE IF NOT EXISTS miscellaneous_fields (
        data_time_stamp TEXT NOT NULL,
        sensor_index INTEGER NOT NULL,
        voc REAL NULL,
        voc_a REAL NULL,
        voc_b REAL NULL,
        ozone1 REAL NULL,
        analog_input REAL NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note: Since we can't have decimals in variable names, we do pm1_0 instead of pm1.0
#: SQLITE statement for pm1_0_fields table
CREATE_PM1_0_FIELDS = """
    CREATE TABLE IF NOT EXISTS pm1_0_fields(
        data_time_stamp TEXT NOT NULL,
        sensor_index INTEGER NOT NULL,
        pm1_0 REAL NULL,
        pm1_0_a REAL NULL,
        pm1_0_b REAL NULL,
        pm1_0_atm REAL NULL,
        pm1_0_atm_a REAL NULL,
        pm1_0_atm_b REAL NULL,
        pm1_0_cf_1 REAL NULL,
        pm1_0_cf_1_a REAL NULL,
        pm1_0_cf_1_b REAL NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note: Since we can't have decimals in variable names, we do pm2_5 instead of pm2.5
#: SQLITE statement for pm2_5_fields table
CREATE_PM2_5_FIELDS = """
    CREATE TABLE IF NOT EXISTS pm2_5_fields (
        data_time_stamp TEXT NOT NULL,
        sensor_index INTEGER NOT NULL,
        pm2_5_alt REAL NULL,
        pm2_5_alt_a REAL NULL,
        pm2_5_alt_b REAL NULL,
        pm2_5 REAL NULL,
        pm2_5_a REAL NULL,
        pm2_5_b REAL NULL,
        pm2_5_atm REAL NULL,
        pm2_5_atm_a REAL NULL,
        pm2_5_atm_b REAL NULL,
        pm2_5_cf_1 REAL NULL,
        pm2_5_cf_1_a REAL NULL,
        pm2_5_cf_1_b REAL NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note: Since we can't have decimals in variable names, we do pm2_5 instead of pm2.5
#: SQLITE statement for pm2_5_pseudo_average_fields table
CREATE_PM2_5_PSEUDO_AVERAGE_FIELDS = """
    CREATE TABLE IF NOT EXISTS pm2_5_pseudo_average_fields (
        data_time_stamp TEXT NOT NULL,
        sensor_index INTEGER NOT NULL,
        pm2_5_10minute REAL NULL,
        pm2_5_10minute_a REAL NULL,
        pm2_5_10minute_b REAL NULL,
        pm2_5_30minute REAL NULL,
        pm2_5_30minute_a REAL NULL,
        pm2_5_30minute_b REAL NULL,
        pm2_5_60minute REAL NULL,
        pm2_5_60minute_a REAL NULL,
        pm2_5_60minute_b REAL NULL,
        pm2_5_6hour REAL NULL,
        pm2_5_6hour_a REAL NULL,
        pm2_5_6hour_b REAL NULL,
        pm2_5_24hour REAL NULL,
        pm2_5_24hour_a REAL NULL,
        pm2_5_24hour_b REAL NULL,
        pm2_5_1week REAL NULL,
        pm2_5_1week_a REAL NULL,
        pm2_5_1week_b REAL NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note: Since we can't have decimals in variable names, we do pm10_0 instead of pm10.0
#: SQLITE statement for pm10_0_fields table
CREATE_PM10_0_FIELDS = """
    CREATE TABLE IF NOT EXISTS pm10_0_fields (
        data_time_stamp TEXT NOT NULL,
        sensor_index INTEGER NOT NULL,
        pm10_0 REAL NULL,
        pm10_0_a REAL NULL,
        pm10_0_b REAL NULL,
        pm10_0_atm REAL NULL,
        pm10_0_atm_a REAL NULL,
        pm10_0_atm_b REAL NULL,
        pm10_0_cf_1 REAL NULL,
        pm10_0_cf_1_a REAL NULL,
        pm10_0_cf_1_b REAL NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note: we can not start column names with numbers. So 0_3_um_count becomes um_count_0_3
#: SQLITE statement for particle_count_fields table
CREATE_PARTICLE_COUNT_FIELDS = """
    CREATE TABLE IF NOT EXISTS particle_count_fields (
        data_time_stamp TEXT NOT NULL,
        sensor_index INTEGER NOT NULL,
        um_count_0_3 REAL NULL,
        um_count_a_0_3 REAL NULL,
        um_count_b_0_3 REAL NULL,
        um_count_0_5 REAL NULL,
        um_count_a_0_5 REAL NULL,
        um_count_b_0_5 REAL NULL,
        um_count_1_0 REAL NULL,
        um_count_a_1_0 REAL NULL,
        um_count_b_1_0 REAL NULL,
        um_count_2_5 REAL NULL,
        um_count_a_2_5 REAL NULL,
        um_count_b_2_5 REAL NULL,
        um_count_5_0 REAL NULL,
        um_count_a_5_0 REAL NULL,
        um_count_b_5_0 REAL NULL,
        um_count_10_0 REAL NULL,
        um_count_a_10_0 REAL NULL,
        um_count_b_10_0 REAL NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

#: Note TO SELF MAY END UP GETTING RID OF THIS TABLE. I SEE NO USE FOR IT.
#: SQLITE statement for thingspeak_fields table
CREATE_THINGSPEAK_FIELDS = """
    CREATE TABLE IF NOT EXISTS thingspeak_fields (
        data_time_stamp TEXT NOT NULL,
        sensor_index INTEGER NOT NULL,
        primary_id_a INTEGER NULL,
        primary_key_a TEXT NULL,
        secondary_id_a INTEGER NULL,
        secondary_key_a TEXT NULL,
        primary_id_b INTEGER NULL,
        primary_key_b TEXT NULL,
        secondary_id_b INTEGER NULL,
        secondary_key_b TEXT NULL,
        PRIMARY KEY(data_time_stamp, sensor_index))"""

# As of 07/23/2022 we have 9 tables to insert data into.
#: SQLITE insert statement for station_information_and_status_fields
SQLITE_INSERT_STATEMENT_STATION_INFORMATION_AND_STATUS_FIELDS = """
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
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )"""

#: SQLITE insert statement for environmental_fields
SQLITE_INSERT_STATEMENT_ENVIRONMENTAL_FIELDS = """
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
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )"""

#: SQLITE insert statement for miscellaneous_fields
SQLITE_INSERT_STATEMENT_MISCELLANEOUS_FIELDS = """
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
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )"""

#: SQLITE insert statement for pm1_0_fields
SQLITE_INSERT_STATEMENT_PM1_0_FIELDS = """
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
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )"""

#: SQLITE insert statement for pm2_5_fields
SQLITE_INSERT_STATEMENT_PM2_5_FIELDS = """
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
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )"""

#: SQLITE insert statement for pm2_5_pseudo_average_fields
SQLITE_INSERT_STATEMENT_PM2_5_PSEUDO_AVERAGE_FIELDS = """
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
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?
    )"""

#: SQLITE insert statement for pm10_0_fields
SQLITE_INSERT_STATEMENT_PM10_0_FIELDS = """
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
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?
    )"""

#: SQLITE insert statement for particle_count_fields
SQLITE_INSERT_STATEMENT_PARTICLE_COUNT_FIELDS = """
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
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?
    )"""

#: SQLITE insert statement for thingspeak_fields
SQLITE_INSERT_STATEMENT_THINGSPEAK_FIELDS = """
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
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?
    )"""

#: SQLITE statement to drop all tables in the database
SQLITE_DROP_ALL_TABLES = """
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
