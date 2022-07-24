#!/usr/bin/env python3

"""
A file containing PSQL statements defined as constants.
"""

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

create_environmental_fields_table = """
    CREATE TABLE IF NOT EXISTS environmental_fields (
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
create_pm1_0_fields = """
    CREATE TABLE IF NOT EXISTS pm1_0_fields(
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
create_pm2_5_fields = """
    CREATE TABLE IF NOT EXISTS pm2_5_fields (
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
create_pm2_5_pseudo_average_fields = """
    CREATE TABLE IF NOT EXISTS pm2_5_pseudo_average_fields (
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
create_pm10_0_fields = """
    CREATE TABLE IF NOT EXISTS pm10_0_fields (
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

psql_insert_statement_environmental_fields = """
    INSERT INTO environmental_fields
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
            pressure_b
        ) 
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

psql_insert_statement_miscellaneous_fields = """
    INSERT INTO miscellaneous_fields
        (
            data_time_stamp,
            voc,
            voc_a,
            voc_b,
            ozone1,
            analog_input
        ) 
        VALUES
        (
            CAST(:data_time_stamp AS TIMESTAMP),
            CAST(:voc AS FLOAT),
            CAST(:voc_a AS FLOAT),
            CAST(:voc_b AS FLOAT),
            CAST(:ozone1 AS FLOAT),
            CAST(:analog_input AS FLOAT)
        )"""

psql_insert_statement_pm1_0_fields = """
    INSERT INTO pm1_0_fields
        (
            data_time_stamp,
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
            CAST(:data_time_stamp AS TIMESTAMP),
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

psql_insert_statement_pm2_5_fields = """
    INSERT INTO pm2_5_fields
        (
            data_time_stamp,
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
            CAST(:data_time_stamp AS TIMESTAMP),
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

psql_insert_statement_pm2_5_pseudo_average_fields = """
    INSERT INTO pm2_5_pseudo_average_fields 
    (
        data_time_stamp,
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
        CAST(:data_time_stamp AS TIMESTAMP),
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

psql_insert_statement_pm10_0_fields = """
    INSERT INTO pm10_0_fields
    (
        data_time_stamp,
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
        CAST(:data_time_stamp AS TIMESTAMP),
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
psql_insert_statement_particle_count_fields = """
    INSERT INTO particle_count_fields 
    (
        data_time_stamp,
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
        CAST(:data_time_stamp AS TIMESTAMP),
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

psql_insert_statement_thingspeak_fields = """
    INSERT INTO thingspeak_fields
    (
        data_time_stamp,
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
        CAST(:data_time_stamp AS TIMESTAMP),
        CAST(:primary_id_a AS INT),
        CAST(:primary_key_a AS TEXT),
        CAST(:secondary_id_a AS INT),
        CAST(:secondary_key_a AS TEXT),
        CAST(:primary_id_b AS INT),
        CAST(:primary_key_b AS TEXT),
        CAST(:secondary_id_b AS INT),
        CAST(:secondary_key_b AS TEXT)
    )"""
