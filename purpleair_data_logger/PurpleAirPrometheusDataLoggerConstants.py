#!/usr/bin/env python3

"""
Copyright 2023 carlkidcrypto, All rights reserved.
A file containing PrometheusDataLogger constants.
"""

#: Default Prometheus HTTP server port
PROMETHEUS_DATA_LOGGER_DEFAULT_PORT = 9760

# ---- Station information and status fields ----

#: Metric name for data_time_stamp
STATION_DATA_TIME_STAMP_METRIC_NAME = "purpleair_station_data_time_stamp"
#: Metric description for data_time_stamp
STATION_DATA_TIME_STAMP_METRIC_DESCRIPTION = (
    "PurpleAir sensor data timestamp (Unix epoch seconds)"
)

#: Metric name for icon
STATION_ICON_METRIC_NAME = "purpleair_station_icon"
#: Metric description for icon
STATION_ICON_METRIC_DESCRIPTION = "PurpleAir sensor icon id"

#: Metric name for location_type
STATION_LOCATION_TYPE_METRIC_NAME = "purpleair_station_location_type"
#: Metric description for location_type
STATION_LOCATION_TYPE_METRIC_DESCRIPTION = (
    "PurpleAir sensor location type (0=outside, 1=inside)"
)

#: Metric name for private
STATION_PRIVATE_METRIC_NAME = "purpleair_station_private"
#: Metric description for private
STATION_PRIVATE_METRIC_DESCRIPTION = "PurpleAir sensor private flag"

#: Metric name for latitude
STATION_LATITUDE_METRIC_NAME = "purpleair_station_latitude"
#: Metric description for latitude
STATION_LATITUDE_METRIC_DESCRIPTION = "PurpleAir sensor latitude"

#: Metric name for longitude
STATION_LONGITUDE_METRIC_NAME = "purpleair_station_longitude"
#: Metric description for longitude
STATION_LONGITUDE_METRIC_DESCRIPTION = "PurpleAir sensor longitude"

#: Metric name for altitude
STATION_ALTITUDE_METRIC_NAME = "purpleair_station_altitude"
#: Metric description for altitude
STATION_ALTITUDE_METRIC_DESCRIPTION = "PurpleAir sensor altitude (feet)"

#: Metric name for position_rating
STATION_POSITION_RATING_METRIC_NAME = "purpleair_station_position_rating"
#: Metric description for position_rating
STATION_POSITION_RATING_METRIC_DESCRIPTION = "PurpleAir sensor GPS position rating"

#: Metric name for led_brightness
STATION_LED_BRIGHTNESS_METRIC_NAME = "purpleair_station_led_brightness"
#: Metric description for led_brightness
STATION_LED_BRIGHTNESS_METRIC_DESCRIPTION = "PurpleAir sensor LED brightness (%)"

#: Metric name for rssi
STATION_RSSI_METRIC_NAME = "purpleair_station_rssi"
#: Metric description for rssi
STATION_RSSI_METRIC_DESCRIPTION = "PurpleAir sensor WiFi RSSI (dBm)"

#: Metric name for uptime
STATION_UPTIME_METRIC_NAME = "purpleair_station_uptime"
#: Metric description for uptime
STATION_UPTIME_METRIC_DESCRIPTION = "PurpleAir sensor uptime (minutes)"

#: Metric name for pa_latency
STATION_PA_LATENCY_METRIC_NAME = "purpleair_station_pa_latency"
#: Metric description for pa_latency
STATION_PA_LATENCY_METRIC_DESCRIPTION = "PurpleAir sensor latency (ms)"

#: Metric name for memory
STATION_MEMORY_METRIC_NAME = "purpleair_station_memory"
#: Metric description for memory
STATION_MEMORY_METRIC_DESCRIPTION = "PurpleAir sensor free memory (bytes)"

#: Metric name for last_seen
STATION_LAST_SEEN_METRIC_NAME = "purpleair_station_last_seen"
#: Metric description for last_seen
STATION_LAST_SEEN_METRIC_DESCRIPTION = (
    "PurpleAir sensor last seen timestamp (Unix epoch seconds)"
)

#: Metric name for last_modified
STATION_LAST_MODIFIED_METRIC_NAME = "purpleair_station_last_modified"
#: Metric description for last_modified
STATION_LAST_MODIFIED_METRIC_DESCRIPTION = (
    "PurpleAir sensor last modified timestamp (Unix epoch seconds)"
)

#: Metric name for date_created
STATION_DATE_CREATED_METRIC_NAME = "purpleair_station_date_created"
#: Metric description for date_created
STATION_DATE_CREATED_METRIC_DESCRIPTION = (
    "PurpleAir sensor date created timestamp (Unix epoch seconds)"
)

#: Metric name for channel_state
STATION_CHANNEL_STATE_METRIC_NAME = "purpleair_station_channel_state"
#: Metric description for channel_state
STATION_CHANNEL_STATE_METRIC_DESCRIPTION = "PurpleAir sensor channel state"

#: Metric name for channel_flags
STATION_CHANNEL_FLAGS_METRIC_NAME = "purpleair_station_channel_flags"
#: Metric description for channel_flags
STATION_CHANNEL_FLAGS_METRIC_DESCRIPTION = "PurpleAir sensor channel flags"

#: Metric name for channel_flags_manual
STATION_CHANNEL_FLAGS_MANUAL_METRIC_NAME = "purpleair_station_channel_flags_manual"
#: Metric description for channel_flags_manual
STATION_CHANNEL_FLAGS_MANUAL_METRIC_DESCRIPTION = (
    "PurpleAir sensor channel flags (manual)"
)

#: Metric name for channel_flags_auto
STATION_CHANNEL_FLAGS_AUTO_METRIC_NAME = "purpleair_station_channel_flags_auto"
#: Metric description for channel_flags_auto
STATION_CHANNEL_FLAGS_AUTO_METRIC_DESCRIPTION = "PurpleAir sensor channel flags (auto)"

#: Metric name for confidence
STATION_CONFIDENCE_METRIC_NAME = "purpleair_station_confidence"
#: Metric description for confidence
STATION_CONFIDENCE_METRIC_DESCRIPTION = "PurpleAir sensor confidence (%)"

#: Metric name for confidence_manual
STATION_CONFIDENCE_MANUAL_METRIC_NAME = "purpleair_station_confidence_manual"
#: Metric description for confidence_manual
STATION_CONFIDENCE_MANUAL_METRIC_DESCRIPTION = (
    "PurpleAir sensor confidence - manual (%)"
)

#: Metric name for confidence_auto
STATION_CONFIDENCE_AUTO_METRIC_NAME = "purpleair_station_confidence_auto"
#: Metric description for confidence_auto
STATION_CONFIDENCE_AUTO_METRIC_DESCRIPTION = "PurpleAir sensor confidence - auto (%)"

# ---- Environmental fields ----

#: Metric name for humidity
ENVIRONMENTAL_HUMIDITY_METRIC_NAME = "purpleair_environmental_humidity"
#: Metric description for humidity
ENVIRONMENTAL_HUMIDITY_METRIC_DESCRIPTION = "PurpleAir sensor humidity (%)"

#: Metric name for humidity_a
ENVIRONMENTAL_HUMIDITY_A_METRIC_NAME = "purpleair_environmental_humidity_a"
#: Metric description for humidity_a
ENVIRONMENTAL_HUMIDITY_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor humidity - channel A (%)"
)

#: Metric name for humidity_b
ENVIRONMENTAL_HUMIDITY_B_METRIC_NAME = "purpleair_environmental_humidity_b"
#: Metric description for humidity_b
ENVIRONMENTAL_HUMIDITY_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor humidity - channel B (%)"
)

#: Metric name for temperature
ENVIRONMENTAL_TEMPERATURE_METRIC_NAME = "purpleair_environmental_temperature"
#: Metric description for temperature
ENVIRONMENTAL_TEMPERATURE_METRIC_DESCRIPTION = "PurpleAir sensor temperature (°F)"

#: Metric name for temperature_a
ENVIRONMENTAL_TEMPERATURE_A_METRIC_NAME = "purpleair_environmental_temperature_a"
#: Metric description for temperature_a
ENVIRONMENTAL_TEMPERATURE_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor temperature - channel A (°F)"
)

#: Metric name for temperature_b
ENVIRONMENTAL_TEMPERATURE_B_METRIC_NAME = "purpleair_environmental_temperature_b"
#: Metric description for temperature_b
ENVIRONMENTAL_TEMPERATURE_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor temperature - channel B (°F)"
)

#: Metric name for pressure
ENVIRONMENTAL_PRESSURE_METRIC_NAME = "purpleair_environmental_pressure"
#: Metric description for pressure
ENVIRONMENTAL_PRESSURE_METRIC_DESCRIPTION = "PurpleAir sensor pressure (hPa)"

#: Metric name for pressure_a
ENVIRONMENTAL_PRESSURE_A_METRIC_NAME = "purpleair_environmental_pressure_a"
#: Metric description for pressure_a
ENVIRONMENTAL_PRESSURE_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor pressure - channel A (hPa)"
)

#: Metric name for pressure_b
ENVIRONMENTAL_PRESSURE_B_METRIC_NAME = "purpleair_environmental_pressure_b"
#: Metric description for pressure_b
ENVIRONMENTAL_PRESSURE_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor pressure - channel B (hPa)"
)

# ---- Miscellaneous fields ----

#: Metric name for voc
MISCELLANEOUS_VOC_METRIC_NAME = "purpleair_miscellaneous_voc"
#: Metric description for voc
MISCELLANEOUS_VOC_METRIC_DESCRIPTION = "PurpleAir sensor VOC (IAQ)"

#: Metric name for voc_a
MISCELLANEOUS_VOC_A_METRIC_NAME = "purpleair_miscellaneous_voc_a"
#: Metric description for voc_a
MISCELLANEOUS_VOC_A_METRIC_DESCRIPTION = "PurpleAir sensor VOC - channel A (IAQ)"

#: Metric name for voc_b
MISCELLANEOUS_VOC_B_METRIC_NAME = "purpleair_miscellaneous_voc_b"
#: Metric description for voc_b
MISCELLANEOUS_VOC_B_METRIC_DESCRIPTION = "PurpleAir sensor VOC - channel B (IAQ)"

#: Metric name for ozone1
MISCELLANEOUS_OZONE1_METRIC_NAME = "purpleair_miscellaneous_ozone1"
#: Metric description for ozone1
MISCELLANEOUS_OZONE1_METRIC_DESCRIPTION = "PurpleAir sensor ozone (ppb)"

#: Metric name for analog_input
MISCELLANEOUS_ANALOG_INPUT_METRIC_NAME = "purpleair_miscellaneous_analog_input"
#: Metric description for analog_input
MISCELLANEOUS_ANALOG_INPUT_METRIC_DESCRIPTION = "PurpleAir sensor analog input (V)"

# ---- PM1.0 fields ----

#: Metric name for pm1.0
PM1_0_METRIC_NAME = "purpleair_pm1_0"
#: Metric description for pm1.0
PM1_0_METRIC_DESCRIPTION = "PurpleAir sensor PM1.0 (μg/m³)"

#: Metric name for pm1.0_a
PM1_0_A_METRIC_NAME = "purpleair_pm1_0_a"
#: Metric description for pm1.0_a
PM1_0_A_METRIC_DESCRIPTION = "PurpleAir sensor PM1.0 - channel A (μg/m³)"

#: Metric name for pm1.0_b
PM1_0_B_METRIC_NAME = "purpleair_pm1_0_b"
#: Metric description for pm1.0_b
PM1_0_B_METRIC_DESCRIPTION = "PurpleAir sensor PM1.0 - channel B (μg/m³)"

#: Metric name for pm1.0_atm
PM1_0_ATM_METRIC_NAME = "purpleair_pm1_0_atm"
#: Metric description for pm1.0_atm
PM1_0_ATM_METRIC_DESCRIPTION = "PurpleAir sensor PM1.0 ATM (μg/m³)"

#: Metric name for pm1.0_atm_a
PM1_0_ATM_A_METRIC_NAME = "purpleair_pm1_0_atm_a"
#: Metric description for pm1.0_atm_a
PM1_0_ATM_A_METRIC_DESCRIPTION = "PurpleAir sensor PM1.0 ATM - channel A (μg/m³)"

#: Metric name for pm1.0_atm_b
PM1_0_ATM_B_METRIC_NAME = "purpleair_pm1_0_atm_b"
#: Metric description for pm1.0_atm_b
PM1_0_ATM_B_METRIC_DESCRIPTION = "PurpleAir sensor PM1.0 ATM - channel B (μg/m³)"

#: Metric name for pm1.0_cf_1
PM1_0_CF_1_METRIC_NAME = "purpleair_pm1_0_cf_1"
#: Metric description for pm1.0_cf_1
PM1_0_CF_1_METRIC_DESCRIPTION = "PurpleAir sensor PM1.0 CF=1 (μg/m³)"

#: Metric name for pm1.0_cf_1_a
PM1_0_CF_1_A_METRIC_NAME = "purpleair_pm1_0_cf_1_a"
#: Metric description for pm1.0_cf_1_a
PM1_0_CF_1_A_METRIC_DESCRIPTION = "PurpleAir sensor PM1.0 CF=1 - channel A (μg/m³)"

#: Metric name for pm1.0_cf_1_b
PM1_0_CF_1_B_METRIC_NAME = "purpleair_pm1_0_cf_1_b"
#: Metric description for pm1.0_cf_1_b
PM1_0_CF_1_B_METRIC_DESCRIPTION = "PurpleAir sensor PM1.0 CF=1 - channel B (μg/m³)"

# ---- PM2.5 fields ----

#: Metric name for pm2.5_alt
PM2_5_ALT_METRIC_NAME = "purpleair_pm2_5_alt"
#: Metric description for pm2.5_alt
PM2_5_ALT_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 ALT (μg/m³)"

#: Metric name for pm2.5_alt_a
PM2_5_ALT_A_METRIC_NAME = "purpleair_pm2_5_alt_a"
#: Metric description for pm2.5_alt_a
PM2_5_ALT_A_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 ALT - channel A (μg/m³)"

#: Metric name for pm2.5_alt_b
PM2_5_ALT_B_METRIC_NAME = "purpleair_pm2_5_alt_b"
#: Metric description for pm2.5_alt_b
PM2_5_ALT_B_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 ALT - channel B (μg/m³)"

#: Metric name for pm2.5
PM2_5_METRIC_NAME = "purpleair_pm2_5"
#: Metric description for pm2.5
PM2_5_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 (μg/m³)"

#: Metric name for pm2.5_a
PM2_5_A_METRIC_NAME = "purpleair_pm2_5_a"
#: Metric description for pm2.5_a
PM2_5_A_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 - channel A (μg/m³)"

#: Metric name for pm2.5_b
PM2_5_B_METRIC_NAME = "purpleair_pm2_5_b"
#: Metric description for pm2.5_b
PM2_5_B_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 - channel B (μg/m³)"

#: Metric name for pm2.5_atm
PM2_5_ATM_METRIC_NAME = "purpleair_pm2_5_atm"
#: Metric description for pm2.5_atm
PM2_5_ATM_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 ATM (μg/m³)"

#: Metric name for pm2.5_atm_a
PM2_5_ATM_A_METRIC_NAME = "purpleair_pm2_5_atm_a"
#: Metric description for pm2.5_atm_a
PM2_5_ATM_A_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 ATM - channel A (μg/m³)"

#: Metric name for pm2.5_atm_b
PM2_5_ATM_B_METRIC_NAME = "purpleair_pm2_5_atm_b"
#: Metric description for pm2.5_atm_b
PM2_5_ATM_B_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 ATM - channel B (μg/m³)"

#: Metric name for pm2.5_cf_1
PM2_5_CF_1_METRIC_NAME = "purpleair_pm2_5_cf_1"
#: Metric description for pm2.5_cf_1
PM2_5_CF_1_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 CF=1 (μg/m³)"

#: Metric name for pm2.5_cf_1_a
PM2_5_CF_1_A_METRIC_NAME = "purpleair_pm2_5_cf_1_a"
#: Metric description for pm2.5_cf_1_a
PM2_5_CF_1_A_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 CF=1 - channel A (μg/m³)"

#: Metric name for pm2.5_cf_1_b
PM2_5_CF_1_B_METRIC_NAME = "purpleair_pm2_5_cf_1_b"
#: Metric description for pm2.5_cf_1_b
PM2_5_CF_1_B_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 CF=1 - channel B (μg/m³)"

# ---- PM2.5 pseudo average fields ----

#: Metric name for pm2.5_10minute
PM2_5_10MINUTE_METRIC_NAME = "purpleair_pm2_5_10minute"
#: Metric description for pm2.5_10minute
PM2_5_10MINUTE_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 10-minute average (μg/m³)"

#: Metric name for pm2.5_10minute_a
PM2_5_10MINUTE_A_METRIC_NAME = "purpleair_pm2_5_10minute_a"
#: Metric description for pm2.5_10minute_a
PM2_5_10MINUTE_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 10-minute average - channel A (μg/m³)"
)

#: Metric name for pm2.5_10minute_b
PM2_5_10MINUTE_B_METRIC_NAME = "purpleair_pm2_5_10minute_b"
#: Metric description for pm2.5_10minute_b
PM2_5_10MINUTE_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 10-minute average - channel B (μg/m³)"
)

#: Metric name for pm2.5_30minute
PM2_5_30MINUTE_METRIC_NAME = "purpleair_pm2_5_30minute"
#: Metric description for pm2.5_30minute
PM2_5_30MINUTE_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 30-minute average (μg/m³)"

#: Metric name for pm2.5_30minute_a
PM2_5_30MINUTE_A_METRIC_NAME = "purpleair_pm2_5_30minute_a"
#: Metric description for pm2.5_30minute_a
PM2_5_30MINUTE_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 30-minute average - channel A (μg/m³)"
)

#: Metric name for pm2.5_30minute_b
PM2_5_30MINUTE_B_METRIC_NAME = "purpleair_pm2_5_30minute_b"
#: Metric description for pm2.5_30minute_b
PM2_5_30MINUTE_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 30-minute average - channel B (μg/m³)"
)

#: Metric name for pm2.5_60minute
PM2_5_60MINUTE_METRIC_NAME = "purpleair_pm2_5_60minute"
#: Metric description for pm2.5_60minute
PM2_5_60MINUTE_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 60-minute average (μg/m³)"

#: Metric name for pm2.5_60minute_a
PM2_5_60MINUTE_A_METRIC_NAME = "purpleair_pm2_5_60minute_a"
#: Metric description for pm2.5_60minute_a
PM2_5_60MINUTE_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 60-minute average - channel A (μg/m³)"
)

#: Metric name for pm2.5_60minute_b
PM2_5_60MINUTE_B_METRIC_NAME = "purpleair_pm2_5_60minute_b"
#: Metric description for pm2.5_60minute_b
PM2_5_60MINUTE_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 60-minute average - channel B (μg/m³)"
)

#: Metric name for pm2.5_6hour
PM2_5_6HOUR_METRIC_NAME = "purpleair_pm2_5_6hour"
#: Metric description for pm2.5_6hour
PM2_5_6HOUR_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 6-hour average (μg/m³)"

#: Metric name for pm2.5_6hour_a
PM2_5_6HOUR_A_METRIC_NAME = "purpleair_pm2_5_6hour_a"
#: Metric description for pm2.5_6hour_a
PM2_5_6HOUR_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 6-hour average - channel A (μg/m³)"
)

#: Metric name for pm2.5_6hour_b
PM2_5_6HOUR_B_METRIC_NAME = "purpleair_pm2_5_6hour_b"
#: Metric description for pm2.5_6hour_b
PM2_5_6HOUR_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 6-hour average - channel B (μg/m³)"
)

#: Metric name for pm2.5_24hour
PM2_5_24HOUR_METRIC_NAME = "purpleair_pm2_5_24hour"
#: Metric description for pm2.5_24hour
PM2_5_24HOUR_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 24-hour average (μg/m³)"

#: Metric name for pm2.5_24hour_a
PM2_5_24HOUR_A_METRIC_NAME = "purpleair_pm2_5_24hour_a"
#: Metric description for pm2.5_24hour_a
PM2_5_24HOUR_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 24-hour average - channel A (μg/m³)"
)

#: Metric name for pm2.5_24hour_b
PM2_5_24HOUR_B_METRIC_NAME = "purpleair_pm2_5_24hour_b"
#: Metric description for pm2.5_24hour_b
PM2_5_24HOUR_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 24-hour average - channel B (μg/m³)"
)

#: Metric name for pm2.5_1week
PM2_5_1WEEK_METRIC_NAME = "purpleair_pm2_5_1week"
#: Metric description for pm2.5_1week
PM2_5_1WEEK_METRIC_DESCRIPTION = "PurpleAir sensor PM2.5 1-week average (μg/m³)"

#: Metric name for pm2.5_1week_a
PM2_5_1WEEK_A_METRIC_NAME = "purpleair_pm2_5_1week_a"
#: Metric description for pm2.5_1week_a
PM2_5_1WEEK_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 1-week average - channel A (μg/m³)"
)

#: Metric name for pm2.5_1week_b
PM2_5_1WEEK_B_METRIC_NAME = "purpleair_pm2_5_1week_b"
#: Metric description for pm2.5_1week_b
PM2_5_1WEEK_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor PM2.5 1-week average - channel B (μg/m³)"
)

# ---- PM10.0 fields ----

#: Metric name for pm10.0
PM10_0_METRIC_NAME = "purpleair_pm10_0"
#: Metric description for pm10.0
PM10_0_METRIC_DESCRIPTION = "PurpleAir sensor PM10.0 (μg/m³)"

#: Metric name for pm10.0_a
PM10_0_A_METRIC_NAME = "purpleair_pm10_0_a"
#: Metric description for pm10.0_a
PM10_0_A_METRIC_DESCRIPTION = "PurpleAir sensor PM10.0 - channel A (μg/m³)"

#: Metric name for pm10.0_b
PM10_0_B_METRIC_NAME = "purpleair_pm10_0_b"
#: Metric description for pm10.0_b
PM10_0_B_METRIC_DESCRIPTION = "PurpleAir sensor PM10.0 - channel B (μg/m³)"

#: Metric name for pm10.0_atm
PM10_0_ATM_METRIC_NAME = "purpleair_pm10_0_atm"
#: Metric description for pm10.0_atm
PM10_0_ATM_METRIC_DESCRIPTION = "PurpleAir sensor PM10.0 ATM (μg/m³)"

#: Metric name for pm10.0_atm_a
PM10_0_ATM_A_METRIC_NAME = "purpleair_pm10_0_atm_a"
#: Metric description for pm10.0_atm_a
PM10_0_ATM_A_METRIC_DESCRIPTION = "PurpleAir sensor PM10.0 ATM - channel A (μg/m³)"

#: Metric name for pm10.0_atm_b
PM10_0_ATM_B_METRIC_NAME = "purpleair_pm10_0_atm_b"
#: Metric description for pm10.0_atm_b
PM10_0_ATM_B_METRIC_DESCRIPTION = "PurpleAir sensor PM10.0 ATM - channel B (μg/m³)"

#: Metric name for pm10.0_cf_1
PM10_0_CF_1_METRIC_NAME = "purpleair_pm10_0_cf_1"
#: Metric description for pm10.0_cf_1
PM10_0_CF_1_METRIC_DESCRIPTION = "PurpleAir sensor PM10.0 CF=1 (μg/m³)"

#: Metric name for pm10.0_cf_1_a
PM10_0_CF_1_A_METRIC_NAME = "purpleair_pm10_0_cf_1_a"
#: Metric description for pm10.0_cf_1_a
PM10_0_CF_1_A_METRIC_DESCRIPTION = "PurpleAir sensor PM10.0 CF=1 - channel A (μg/m³)"

#: Metric name for pm10.0_cf_1_b
PM10_0_CF_1_B_METRIC_NAME = "purpleair_pm10_0_cf_1_b"
#: Metric description for pm10.0_cf_1_b
PM10_0_CF_1_B_METRIC_DESCRIPTION = "PurpleAir sensor PM10.0 CF=1 - channel B (μg/m³)"

# ---- Particle count fields ----

#: Metric name for 0.3_um_count
UM_COUNT_0_3_METRIC_NAME = "purpleair_0_3_um_count"
#: Metric description for 0.3_um_count
UM_COUNT_0_3_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >0.3 μm (particles/dl)"
)

#: Metric name for 0.3_um_count_a
UM_COUNT_0_3_A_METRIC_NAME = "purpleair_0_3_um_count_a"
#: Metric description for 0.3_um_count_a
UM_COUNT_0_3_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >0.3 μm - channel A (particles/dl)"
)

#: Metric name for 0.3_um_count_b
UM_COUNT_0_3_B_METRIC_NAME = "purpleair_0_3_um_count_b"
#: Metric description for 0.3_um_count_b
UM_COUNT_0_3_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >0.3 μm - channel B (particles/dl)"
)

#: Metric name for 0.5_um_count
UM_COUNT_0_5_METRIC_NAME = "purpleair_0_5_um_count"
#: Metric description for 0.5_um_count
UM_COUNT_0_5_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >0.5 μm (particles/dl)"
)

#: Metric name for 0.5_um_count_a
UM_COUNT_0_5_A_METRIC_NAME = "purpleair_0_5_um_count_a"
#: Metric description for 0.5_um_count_a
UM_COUNT_0_5_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >0.5 μm - channel A (particles/dl)"
)

#: Metric name for 0.5_um_count_b
UM_COUNT_0_5_B_METRIC_NAME = "purpleair_0_5_um_count_b"
#: Metric description for 0.5_um_count_b
UM_COUNT_0_5_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >0.5 μm - channel B (particles/dl)"
)

#: Metric name for 1.0_um_count
UM_COUNT_1_0_METRIC_NAME = "purpleair_1_0_um_count"
#: Metric description for 1.0_um_count
UM_COUNT_1_0_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >1.0 μm (particles/dl)"
)

#: Metric name for 1.0_um_count_a
UM_COUNT_1_0_A_METRIC_NAME = "purpleair_1_0_um_count_a"
#: Metric description for 1.0_um_count_a
UM_COUNT_1_0_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >1.0 μm - channel A (particles/dl)"
)

#: Metric name for 1.0_um_count_b
UM_COUNT_1_0_B_METRIC_NAME = "purpleair_1_0_um_count_b"
#: Metric description for 1.0_um_count_b
UM_COUNT_1_0_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >1.0 μm - channel B (particles/dl)"
)

#: Metric name for 2.5_um_count
UM_COUNT_2_5_METRIC_NAME = "purpleair_2_5_um_count"
#: Metric description for 2.5_um_count
UM_COUNT_2_5_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >2.5 μm (particles/dl)"
)

#: Metric name for 2.5_um_count_a
UM_COUNT_2_5_A_METRIC_NAME = "purpleair_2_5_um_count_a"
#: Metric description for 2.5_um_count_a
UM_COUNT_2_5_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >2.5 μm - channel A (particles/dl)"
)

#: Metric name for 2.5_um_count_b
UM_COUNT_2_5_B_METRIC_NAME = "purpleair_2_5_um_count_b"
#: Metric description for 2.5_um_count_b
UM_COUNT_2_5_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >2.5 μm - channel B (particles/dl)"
)

#: Metric name for 5.0_um_count
UM_COUNT_5_0_METRIC_NAME = "purpleair_5_0_um_count"
#: Metric description for 5.0_um_count
UM_COUNT_5_0_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >5.0 μm (particles/dl)"
)

#: Metric name for 5.0_um_count_a
UM_COUNT_5_0_A_METRIC_NAME = "purpleair_5_0_um_count_a"
#: Metric description for 5.0_um_count_a
UM_COUNT_5_0_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >5.0 μm - channel A (particles/dl)"
)

#: Metric name for 5.0_um_count_b
UM_COUNT_5_0_B_METRIC_NAME = "purpleair_5_0_um_count_b"
#: Metric description for 5.0_um_count_b
UM_COUNT_5_0_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >5.0 μm - channel B (particles/dl)"
)

#: Metric name for 10.0_um_count
UM_COUNT_10_0_METRIC_NAME = "purpleair_10_0_um_count"
#: Metric description for 10.0_um_count
UM_COUNT_10_0_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >10.0 μm (particles/dl)"
)

#: Metric name for 10.0_um_count_a
UM_COUNT_10_0_A_METRIC_NAME = "purpleair_10_0_um_count_a"
#: Metric description for 10.0_um_count_a
UM_COUNT_10_0_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >10.0 μm - channel A (particles/dl)"
)

#: Metric name for 10.0_um_count_b
UM_COUNT_10_0_B_METRIC_NAME = "purpleair_10_0_um_count_b"
#: Metric description for 10.0_um_count_b
UM_COUNT_10_0_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor particle count >10.0 μm - channel B (particles/dl)"
)

# ---- ThingSpeak fields ----

#: Metric name for primary_id_a
THINGSPEAK_PRIMARY_ID_A_METRIC_NAME = "purpleair_thingspeak_primary_id_a"
#: Metric description for primary_id_a
THINGSPEAK_PRIMARY_ID_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor ThingSpeak primary channel ID - channel A"
)

#: Metric name for secondary_id_a
THINGSPEAK_SECONDARY_ID_A_METRIC_NAME = "purpleair_thingspeak_secondary_id_a"
#: Metric description for secondary_id_a
THINGSPEAK_SECONDARY_ID_A_METRIC_DESCRIPTION = (
    "PurpleAir sensor ThingSpeak secondary channel ID - channel A"
)

#: Metric name for primary_id_b
THINGSPEAK_PRIMARY_ID_B_METRIC_NAME = "purpleair_thingspeak_primary_id_b"
#: Metric description for primary_id_b
THINGSPEAK_PRIMARY_ID_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor ThingSpeak primary channel ID - channel B"
)

#: Metric name for secondary_id_b
THINGSPEAK_SECONDARY_ID_B_METRIC_NAME = "purpleair_thingspeak_secondary_id_b"
#: Metric description for secondary_id_b
THINGSPEAK_SECONDARY_ID_B_METRIC_DESCRIPTION = (
    "PurpleAir sensor ThingSpeak secondary channel ID - channel B"
)
