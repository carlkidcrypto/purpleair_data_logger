#!/usr/bin/env python3

"""
    Copyright 2022 carlkid1499, All rights reserved.
    A python with constants with for use in PurpleAirAPI.py
"""

#: A constant to see if debug statements are enabled in the PurpleAirAPI module.
PRINT_DEBUG_MSGS = True

#: Store the dict/json keys to access data fields.
#: These keys are derived from the PurpleAir documentation: https://api.purpleair.com/#api-sensors-get-sensor-data
ACCEPTED_FIELD_NAMES_LIST = [
    # Station information and status fields:
    "name", "icon", "model", "hardware", "location_type", "private", "latitude", "longitude", "altitude", "position_rating", "led_brightness", "firmware_version", "firmware_upgrade", "rssi", "uptime", "pa_latency", "memory", "last_seen", "last_modified", "date_created", "channel_state", "channel_flags", "channel_flags_manual", "channel_flags_auto", "confidence", "confidence_manual", "confidence_auto",

    # Environmental fields:
    "humidity", "humidity_a", "humidity_b", "temperature", "temperature_a", "temperature_b", "pressure", "pressure_a", "pressure_b",

    # Miscellaneous fields:
    "voc", "voc_a", "voc_b", "ozone1", "analog_input",

    # PM1.0 fields:
    "pm1.0", "pm1.0_a", "pm1.0_b", "pm1.0_atm", "pm1.0_atm_a", "pm1.0_atm_b", "pm1.0_cf_1", "pm1.0_cf_1_a",
    "pm1.0_cf_1_b",

    # PM2.5 fields:
    "pm2.5_alt", "pm2.5_alt_a", "pm2.5_alt_b", "pm2.5", "pm2.5_a", "pm2.5_b", "pm2.5_atm", "pm2.5_atm_a", "pm2.5_atm_b", "pm2.5_cf_1", "pm2.5_cf_1_a", "pm2.5_cf_1_b",

    # PM2.5 pseudo (simple running) average fields:
    # Note: These are inside the return json as json["sensor"]["stats"]. They are averages of the two sensors.
    # sensor 'a' and 'b' sensor be. Each sensors data is inside json["sensor"]["stats_a"] and json["sensor"]["stats_b"]
    "pm2.5_10minute", "pm2.5_10minute_a", "pm2.5_10minute_b", "pm2.5_30minute", "pm2.5_30minute_a", "pm2.5_30minute_b", "pm2.5_60minute", "pm2.5_60minute_a", "pm2.5_60minute_b", "pm2.5_6hour", "pm2.5_6hour_a", "pm2.5_6hour_b",
    "pm2.5_24hour", "pm2.5_24hour_a", "pm2.5_24hour_b", "pm2.5_1week", "pm2.5_1week_a", "pm2.5_1week_b",

    # PM10.0 fields:
    "pm10.0", "pm10.0_a", "pm10.0_b", "pm10.0_atm", "pm10.0_atm_a", "pm10.0_atm_b", "pm10.0_cf_1", "pm10.0_cf_1_a", "pm10.0_cf_1_b",

    # Particle count fields:
    "0.3_um_count", "0.3_um_count_a", "0.3_um_count_b", "0.5_um_count", "0.5_um_count_a", "0.5_um_count_b", "1.0_um_count", "1.0_um_count_a", "1.0_um_count_b", "2.5_um_count", "2.5_um_count_a", "2.5_um_count_b", "5.0_um_count", "5.0_um_count_a", "5.0_um_count_b", "10.0_um_count", "10.0_um_count_a", "10.0_um_count_b",

    # ThingSpeak fields, used to retrieve data from api.thingspeak.com:
    "primary_id_a", "primary_key_a", "secondary_id_a", "secondary_key_a", "primary_id_b", "primary_key_b", "secondary_id_b", "secondary_key_b"
]
