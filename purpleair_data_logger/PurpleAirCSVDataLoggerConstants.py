#!/usr/bin/env python3

"""
    Copyright 2022 carlkid1499, All rights reserved.
    A file containing CSVDataLogger constants.
"""

#: PSQL statement for station_information_and_status_fields table
STATION_INFORMATION_AND_STATUS_FIELDS_FILE_NAME = """station_information_and_status_fields.csv"""

#: PSQL statement for station_information_and_status_fields table
STATION_INFORMATION_AND_STATUS_FIELDS_HEADER = "\
        data_time_stamp,\
        sensor_index,\
        name,\
        icon,\
        model,\
        hardware,\
        location_type,\
        private,\
        latitude,\
        longitude,\
        altitude,\
        position_rating,\
        led_brightness,\
        firmware_version,\
        firmware_upgrade,\
        rssi,\
        uptime,\
        pa_latency,\
        memory,\
        last_seen,\
        last_modified,\
        date_created,\
        channel_state,\
        channel_flags,\
        channel_flags_manual,\
        channel_flags_auto,\
        confidence,\
        confidence_manual,\
        confidence_auto"

#: PSQL statement for environmental_fields table
ENVIRONMENTAL_FIELDS_FILE_NAME = """environmental_fields.csv"""

#: PSQL statement for environmental_fields table
ENVIRONMENTAL_FIELDS_HEADER = "\
        data_time_stamp,\
        sensor_index,\
        humidity,\
        humidity_a,\
        humidity_b,\
        temperature,\
        temperature_a,\
        temperature_b,\
        pressure,\
        pressure_a,\
        pressure_b"

#: PSQL statement for miscellaneous_fields table
MISCELLANEOUS_FIELDS_FILE_NAME = """miscellaneous_fields.csv"""

#: PSQL statement for miscellaneous_fields table
MISCELLANEOUS_FIELDS_HEADER = "\
        data_time_stamp,\
        sensor_index,\
        voc,\
        voc_a,\
        voc_b,\
        ozone1,\
        analog_input"

#: Note: Since we can't have decimals in variable names, we do pm1_0 instead of pm1.0
PM1_0_FIELDS_FILE_NAME = """pm1.0_fields.csv"""

PM1_0_FIELDS_HEADER = "\
        data_time_stamp,\
        sensor_index,\
        pm1.0,\
        pm1.0_a,\
        pm1.0_b,\
        pm1.0_atm,\
        pm1.0_atm_a,\
        pm1.0_atm_b,\
        pm1.0_cf_1,\
        pm1.0_cf_1_a,\
        pm1.0_cf_1_b"

#: Note: Since we can't have decimals in variable names, we do pm2_5 instead of pm2.5
#: PSQL statement for pm2_5_fields table
PM2_5_FIELDS = """pm2.5_fields.csv"""

PM2_5_FIELDS = "\
        data_time_stamp,\
        sensor_index,\
        pm2.5_alt,\
        pm2.5_alt_a,\
        pm2.5_alt_b,\
        pm2.5,\
        pm2.5_a,\
        pm2.5_b,\
        pm2.5_atm,\
        pm2.5_atm_a,\
        pm2.5_atm_b,\
        pm2.5_cf_1,\
        pm2.5_cf_1_a,\
        pm2.5_cf_1_b"

#: Note: Since we can't have decimals in variable names, we do pm2_5 instead of pm2.5
#: PSQL statement for pm2_5_pseudo_average_fields table
PM2_5_PSEUDO_AVERAGE_FIELDS_FILE_NAME = """pm2.5_pseudo_average_fields.csv"""

#: Note: Since we can't have decimals in variable names, we do pm2_5 instead of pm2.5
#: PSQL statement for pm2_5_pseudo_average_fields table
PM2_5_PSEUDO_AVERAGE_FIELDS_HEADER = "\
        data_time_stamp,\
        sensor_index,\
        pm2.5_10minute,\
        pm2.5_10minute_a,\
        pm2.5_10minute_b,\
        pm2.5_30minute,\
        pm2.5_30minute_a,\
        pm2.5_30minute_b,\
        pm2.5_60minute,\
        pm2.5_60minute_a,\
        pm2.5_60minute_b,\
        pm2.5_6hour,\
        pm2.5_6hour_a,\
        pm2.5_6hour_b,\
        pm2.5_24hour,\
        pm2.5_24hour_a,\
        pm2.5_24hour_b,\
        pm2.5_1week,\
        pm2.5_1week_a,\
        pm2.5_1week_b"

#: Note: Since we can't have decimals in variable names, we do pm10_0 instead of pm10.0
#: PSQL statement for pm10_0_fields table
PM10_0_FIELDS_FILE_NAME = """pm10.0_fields.csv"""

#: Note: Since we can't have decimals in variable names, we do pm10_0 instead of pm10.0
#: PSQL statement for pm10_0_fields table
PM10_0_FIELDS_HEADER = "\
        data_time_stamp,\
        sensor_index,\
        pm10.0,\
        pm10.0_a,\
        pm10.0_b,\
        pm10.0_atm,\
        pm10.0_atm_a,\
        pm10.0_atm_b,\
        pm10.0_cf_1,\
        pm10.0_cf_1_a,\
        pm10.0_cf_1_b"

#: Note: we can not start column names with numbers. So 0_3_um_count becomes um_count_0_3
#: PSQL statement for particle_count_fields table
PARTICLE_COUNT_FIELDS_FILE_NAME = """particle_count_fields.csv"""

#: Note: we can not start column names with numbers. So 0_3_um_count becomes um_count_0_3
#: PSQL statement for particle_count_fields table
PARTICLE_COUNT_FIELDS = "\
        data_time_stamp,\
        sensor_index,\
        0.3_um_count,\
        0.3_um_count_a,\
        0.3_um_count_b,\
        0.5_um_count,\
        0.5_um_count_a,\
        0.5_um_count_b,\
        1.0_um_count,\
        1.0_um_count_a,\
        1.0_um_count_b,\
        2.5_um_count,\
        2.5_um_count_a,\
        2.5_um_count_b,\
        5.0_um_count,\
        5.0_um_count_a,\
        5.0_um_count_b,\
        10.0_um_count,\
        10.0_um_count_a,\
        10.0_um_count_b"

#: Note TO SELF MAY END UP GETTING RID OF THIS TABLE. I SEE NO USE FOR IT.
#: PSQL statement for thingspeak_fields table
THINGSPEAK_FIELDS_FILE_NAME = """thingspeak_fields.csv"""

#: Note TO SELF MAY END UP GETTING RID OF THIS TABLE. I SEE NO USE FOR IT.
#: PSQL statement for thingspeak_fields table
THINGSPEAK_FIELDS_HEADER = "\
        data_time_stamp,\
        sensor_index,\
        primary_id_a,\
        primary_key_a,\
        secondary_id_a,\
        secondary_key_a,\
        primary_id_b,\
        primary_key_b,\
        secondary_id_b,\
        secondary_key_b"
