#!/usr/bin/env python3

"""
Copyright 2023 carlkidcrypto, All rights reserved.
A python class designed to use the PurpleAirAPI for requesting sensor(s) data.
Data will be exposed via a Prometheus-compatible HTTP endpoint.

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

from purpleair_data_logger.PurpleAirPrometheusDataLoggerConstants import (
    PROMETHEUS_DATA_LOGGER_DEFAULT_PORT,
    STATION_DATA_TIME_STAMP_METRIC_NAME,
    STATION_DATA_TIME_STAMP_METRIC_DESCRIPTION,
    STATION_ICON_METRIC_NAME,
    STATION_ICON_METRIC_DESCRIPTION,
    STATION_LOCATION_TYPE_METRIC_NAME,
    STATION_LOCATION_TYPE_METRIC_DESCRIPTION,
    STATION_PRIVATE_METRIC_NAME,
    STATION_PRIVATE_METRIC_DESCRIPTION,
    STATION_LATITUDE_METRIC_NAME,
    STATION_LATITUDE_METRIC_DESCRIPTION,
    STATION_LONGITUDE_METRIC_NAME,
    STATION_LONGITUDE_METRIC_DESCRIPTION,
    STATION_ALTITUDE_METRIC_NAME,
    STATION_ALTITUDE_METRIC_DESCRIPTION,
    STATION_POSITION_RATING_METRIC_NAME,
    STATION_POSITION_RATING_METRIC_DESCRIPTION,
    STATION_LED_BRIGHTNESS_METRIC_NAME,
    STATION_LED_BRIGHTNESS_METRIC_DESCRIPTION,
    STATION_RSSI_METRIC_NAME,
    STATION_RSSI_METRIC_DESCRIPTION,
    STATION_UPTIME_METRIC_NAME,
    STATION_UPTIME_METRIC_DESCRIPTION,
    STATION_PA_LATENCY_METRIC_NAME,
    STATION_PA_LATENCY_METRIC_DESCRIPTION,
    STATION_MEMORY_METRIC_NAME,
    STATION_MEMORY_METRIC_DESCRIPTION,
    STATION_LAST_SEEN_METRIC_NAME,
    STATION_LAST_SEEN_METRIC_DESCRIPTION,
    STATION_LAST_MODIFIED_METRIC_NAME,
    STATION_LAST_MODIFIED_METRIC_DESCRIPTION,
    STATION_DATE_CREATED_METRIC_NAME,
    STATION_DATE_CREATED_METRIC_DESCRIPTION,
    STATION_CHANNEL_STATE_METRIC_NAME,
    STATION_CHANNEL_STATE_METRIC_DESCRIPTION,
    STATION_CHANNEL_FLAGS_METRIC_NAME,
    STATION_CHANNEL_FLAGS_METRIC_DESCRIPTION,
    STATION_CHANNEL_FLAGS_MANUAL_METRIC_NAME,
    STATION_CHANNEL_FLAGS_MANUAL_METRIC_DESCRIPTION,
    STATION_CHANNEL_FLAGS_AUTO_METRIC_NAME,
    STATION_CHANNEL_FLAGS_AUTO_METRIC_DESCRIPTION,
    STATION_CONFIDENCE_METRIC_NAME,
    STATION_CONFIDENCE_METRIC_DESCRIPTION,
    STATION_CONFIDENCE_MANUAL_METRIC_NAME,
    STATION_CONFIDENCE_MANUAL_METRIC_DESCRIPTION,
    STATION_CONFIDENCE_AUTO_METRIC_NAME,
    STATION_CONFIDENCE_AUTO_METRIC_DESCRIPTION,
    ENVIRONMENTAL_HUMIDITY_METRIC_NAME,
    ENVIRONMENTAL_HUMIDITY_METRIC_DESCRIPTION,
    ENVIRONMENTAL_HUMIDITY_A_METRIC_NAME,
    ENVIRONMENTAL_HUMIDITY_A_METRIC_DESCRIPTION,
    ENVIRONMENTAL_HUMIDITY_B_METRIC_NAME,
    ENVIRONMENTAL_HUMIDITY_B_METRIC_DESCRIPTION,
    ENVIRONMENTAL_TEMPERATURE_METRIC_NAME,
    ENVIRONMENTAL_TEMPERATURE_METRIC_DESCRIPTION,
    ENVIRONMENTAL_TEMPERATURE_A_METRIC_NAME,
    ENVIRONMENTAL_TEMPERATURE_A_METRIC_DESCRIPTION,
    ENVIRONMENTAL_TEMPERATURE_B_METRIC_NAME,
    ENVIRONMENTAL_TEMPERATURE_B_METRIC_DESCRIPTION,
    ENVIRONMENTAL_PRESSURE_METRIC_NAME,
    ENVIRONMENTAL_PRESSURE_METRIC_DESCRIPTION,
    ENVIRONMENTAL_PRESSURE_A_METRIC_NAME,
    ENVIRONMENTAL_PRESSURE_A_METRIC_DESCRIPTION,
    ENVIRONMENTAL_PRESSURE_B_METRIC_NAME,
    ENVIRONMENTAL_PRESSURE_B_METRIC_DESCRIPTION,
    MISCELLANEOUS_VOC_METRIC_NAME,
    MISCELLANEOUS_VOC_METRIC_DESCRIPTION,
    MISCELLANEOUS_VOC_A_METRIC_NAME,
    MISCELLANEOUS_VOC_A_METRIC_DESCRIPTION,
    MISCELLANEOUS_VOC_B_METRIC_NAME,
    MISCELLANEOUS_VOC_B_METRIC_DESCRIPTION,
    MISCELLANEOUS_OZONE1_METRIC_NAME,
    MISCELLANEOUS_OZONE1_METRIC_DESCRIPTION,
    MISCELLANEOUS_ANALOG_INPUT_METRIC_NAME,
    MISCELLANEOUS_ANALOG_INPUT_METRIC_DESCRIPTION,
    PM1_0_METRIC_NAME,
    PM1_0_METRIC_DESCRIPTION,
    PM1_0_A_METRIC_NAME,
    PM1_0_A_METRIC_DESCRIPTION,
    PM1_0_B_METRIC_NAME,
    PM1_0_B_METRIC_DESCRIPTION,
    PM1_0_ATM_METRIC_NAME,
    PM1_0_ATM_METRIC_DESCRIPTION,
    PM1_0_ATM_A_METRIC_NAME,
    PM1_0_ATM_A_METRIC_DESCRIPTION,
    PM1_0_ATM_B_METRIC_NAME,
    PM1_0_ATM_B_METRIC_DESCRIPTION,
    PM1_0_CF_1_METRIC_NAME,
    PM1_0_CF_1_METRIC_DESCRIPTION,
    PM1_0_CF_1_A_METRIC_NAME,
    PM1_0_CF_1_A_METRIC_DESCRIPTION,
    PM1_0_CF_1_B_METRIC_NAME,
    PM1_0_CF_1_B_METRIC_DESCRIPTION,
    PM2_5_ALT_METRIC_NAME,
    PM2_5_ALT_METRIC_DESCRIPTION,
    PM2_5_ALT_A_METRIC_NAME,
    PM2_5_ALT_A_METRIC_DESCRIPTION,
    PM2_5_ALT_B_METRIC_NAME,
    PM2_5_ALT_B_METRIC_DESCRIPTION,
    PM2_5_METRIC_NAME,
    PM2_5_METRIC_DESCRIPTION,
    PM2_5_A_METRIC_NAME,
    PM2_5_A_METRIC_DESCRIPTION,
    PM2_5_B_METRIC_NAME,
    PM2_5_B_METRIC_DESCRIPTION,
    PM2_5_ATM_METRIC_NAME,
    PM2_5_ATM_METRIC_DESCRIPTION,
    PM2_5_ATM_A_METRIC_NAME,
    PM2_5_ATM_A_METRIC_DESCRIPTION,
    PM2_5_ATM_B_METRIC_NAME,
    PM2_5_ATM_B_METRIC_DESCRIPTION,
    PM2_5_CF_1_METRIC_NAME,
    PM2_5_CF_1_METRIC_DESCRIPTION,
    PM2_5_CF_1_A_METRIC_NAME,
    PM2_5_CF_1_A_METRIC_DESCRIPTION,
    PM2_5_CF_1_B_METRIC_NAME,
    PM2_5_CF_1_B_METRIC_DESCRIPTION,
    PM2_5_10MINUTE_METRIC_NAME,
    PM2_5_10MINUTE_METRIC_DESCRIPTION,
    PM2_5_10MINUTE_A_METRIC_NAME,
    PM2_5_10MINUTE_A_METRIC_DESCRIPTION,
    PM2_5_10MINUTE_B_METRIC_NAME,
    PM2_5_10MINUTE_B_METRIC_DESCRIPTION,
    PM2_5_30MINUTE_METRIC_NAME,
    PM2_5_30MINUTE_METRIC_DESCRIPTION,
    PM2_5_30MINUTE_A_METRIC_NAME,
    PM2_5_30MINUTE_A_METRIC_DESCRIPTION,
    PM2_5_30MINUTE_B_METRIC_NAME,
    PM2_5_30MINUTE_B_METRIC_DESCRIPTION,
    PM2_5_60MINUTE_METRIC_NAME,
    PM2_5_60MINUTE_METRIC_DESCRIPTION,
    PM2_5_60MINUTE_A_METRIC_NAME,
    PM2_5_60MINUTE_A_METRIC_DESCRIPTION,
    PM2_5_60MINUTE_B_METRIC_NAME,
    PM2_5_60MINUTE_B_METRIC_DESCRIPTION,
    PM2_5_6HOUR_METRIC_NAME,
    PM2_5_6HOUR_METRIC_DESCRIPTION,
    PM2_5_6HOUR_A_METRIC_NAME,
    PM2_5_6HOUR_A_METRIC_DESCRIPTION,
    PM2_5_6HOUR_B_METRIC_NAME,
    PM2_5_6HOUR_B_METRIC_DESCRIPTION,
    PM2_5_24HOUR_METRIC_NAME,
    PM2_5_24HOUR_METRIC_DESCRIPTION,
    PM2_5_24HOUR_A_METRIC_NAME,
    PM2_5_24HOUR_A_METRIC_DESCRIPTION,
    PM2_5_24HOUR_B_METRIC_NAME,
    PM2_5_24HOUR_B_METRIC_DESCRIPTION,
    PM2_5_1WEEK_METRIC_NAME,
    PM2_5_1WEEK_METRIC_DESCRIPTION,
    PM2_5_1WEEK_A_METRIC_NAME,
    PM2_5_1WEEK_A_METRIC_DESCRIPTION,
    PM2_5_1WEEK_B_METRIC_NAME,
    PM2_5_1WEEK_B_METRIC_DESCRIPTION,
    PM10_0_METRIC_NAME,
    PM10_0_METRIC_DESCRIPTION,
    PM10_0_A_METRIC_NAME,
    PM10_0_A_METRIC_DESCRIPTION,
    PM10_0_B_METRIC_NAME,
    PM10_0_B_METRIC_DESCRIPTION,
    PM10_0_ATM_METRIC_NAME,
    PM10_0_ATM_METRIC_DESCRIPTION,
    PM10_0_ATM_A_METRIC_NAME,
    PM10_0_ATM_A_METRIC_DESCRIPTION,
    PM10_0_ATM_B_METRIC_NAME,
    PM10_0_ATM_B_METRIC_DESCRIPTION,
    PM10_0_CF_1_METRIC_NAME,
    PM10_0_CF_1_METRIC_DESCRIPTION,
    PM10_0_CF_1_A_METRIC_NAME,
    PM10_0_CF_1_A_METRIC_DESCRIPTION,
    PM10_0_CF_1_B_METRIC_NAME,
    PM10_0_CF_1_B_METRIC_DESCRIPTION,
    UM_COUNT_0_3_METRIC_NAME,
    UM_COUNT_0_3_METRIC_DESCRIPTION,
    UM_COUNT_0_3_A_METRIC_NAME,
    UM_COUNT_0_3_A_METRIC_DESCRIPTION,
    UM_COUNT_0_3_B_METRIC_NAME,
    UM_COUNT_0_3_B_METRIC_DESCRIPTION,
    UM_COUNT_0_5_METRIC_NAME,
    UM_COUNT_0_5_METRIC_DESCRIPTION,
    UM_COUNT_0_5_A_METRIC_NAME,
    UM_COUNT_0_5_A_METRIC_DESCRIPTION,
    UM_COUNT_0_5_B_METRIC_NAME,
    UM_COUNT_0_5_B_METRIC_DESCRIPTION,
    UM_COUNT_1_0_METRIC_NAME,
    UM_COUNT_1_0_METRIC_DESCRIPTION,
    UM_COUNT_1_0_A_METRIC_NAME,
    UM_COUNT_1_0_A_METRIC_DESCRIPTION,
    UM_COUNT_1_0_B_METRIC_NAME,
    UM_COUNT_1_0_B_METRIC_DESCRIPTION,
    UM_COUNT_2_5_METRIC_NAME,
    UM_COUNT_2_5_METRIC_DESCRIPTION,
    UM_COUNT_2_5_A_METRIC_NAME,
    UM_COUNT_2_5_A_METRIC_DESCRIPTION,
    UM_COUNT_2_5_B_METRIC_NAME,
    UM_COUNT_2_5_B_METRIC_DESCRIPTION,
    UM_COUNT_5_0_METRIC_NAME,
    UM_COUNT_5_0_METRIC_DESCRIPTION,
    UM_COUNT_5_0_A_METRIC_NAME,
    UM_COUNT_5_0_A_METRIC_DESCRIPTION,
    UM_COUNT_5_0_B_METRIC_NAME,
    UM_COUNT_5_0_B_METRIC_DESCRIPTION,
    UM_COUNT_10_0_METRIC_NAME,
    UM_COUNT_10_0_METRIC_DESCRIPTION,
    UM_COUNT_10_0_A_METRIC_NAME,
    UM_COUNT_10_0_A_METRIC_DESCRIPTION,
    UM_COUNT_10_0_B_METRIC_NAME,
    UM_COUNT_10_0_B_METRIC_DESCRIPTION,
    THINGSPEAK_PRIMARY_ID_A_METRIC_NAME,
    THINGSPEAK_PRIMARY_ID_A_METRIC_DESCRIPTION,
    THINGSPEAK_SECONDARY_ID_A_METRIC_NAME,
    THINGSPEAK_SECONDARY_ID_A_METRIC_DESCRIPTION,
    THINGSPEAK_PRIMARY_ID_B_METRIC_NAME,
    THINGSPEAK_PRIMARY_ID_B_METRIC_DESCRIPTION,
    THINGSPEAK_SECONDARY_ID_B_METRIC_NAME,
    THINGSPEAK_SECONDARY_ID_B_METRIC_DESCRIPTION,
)

from prometheus_client import Gauge, start_http_server, CollectorRegistry, REGISTRY


class PurpleAirPrometheusDataLogger(PurpleAirDataLogger):
    """
    A data logger class that exposes PurpleAir sensor data as Prometheus metrics.
    Each numeric sensor field is represented as a Gauge with a 'sensor_index' label,
    allowing multiple sensors to share the same metric names.
    """

    def __init__(
        self,
        PurpleAirApiReadKey=None,
        PurpleAirApiWriteKey=None,
        PurpleAirApiIpv4Address=None,
        prometheus_port=PROMETHEUS_DATA_LOGGER_DEFAULT_PORT,
        registry=REGISTRY,
    ):
        """
        :param str PurpleAirApiReadKey: A valid PurpleAirAPI Read key
        :param str PurpleAirApiWriteKey: A valid PurpleAirAPI Write key
        :param list PurpleAirApiIpv4Address: A list of valid IPv4 string addresses with no CIDR's.
        :param int prometheus_port: The TCP port on which the Prometheus HTTP endpoint will listen.
        :param CollectorRegistry registry: The Prometheus registry to register metrics with.
                                           Defaults to the global REGISTRY. Pass a custom
                                           CollectorRegistry instance to isolate metrics (e.g. in tests).
        """

        # Inherit everything from the parent base class: PurpleAirDataLogger
        super().__init__(
            PurpleAirApiReadKey, PurpleAirApiWriteKey, PurpleAirApiIpv4Address
        )

        self._prometheus_port = prometheus_port
        self._registry = registry

        # ---- Station information and status fields ----
        self._station_data_time_stamp = Gauge(
            STATION_DATA_TIME_STAMP_METRIC_NAME,
            STATION_DATA_TIME_STAMP_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_icon = Gauge(
            STATION_ICON_METRIC_NAME,
            STATION_ICON_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_location_type = Gauge(
            STATION_LOCATION_TYPE_METRIC_NAME,
            STATION_LOCATION_TYPE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_private = Gauge(
            STATION_PRIVATE_METRIC_NAME,
            STATION_PRIVATE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_latitude = Gauge(
            STATION_LATITUDE_METRIC_NAME,
            STATION_LATITUDE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_longitude = Gauge(
            STATION_LONGITUDE_METRIC_NAME,
            STATION_LONGITUDE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_altitude = Gauge(
            STATION_ALTITUDE_METRIC_NAME,
            STATION_ALTITUDE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_position_rating = Gauge(
            STATION_POSITION_RATING_METRIC_NAME,
            STATION_POSITION_RATING_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_led_brightness = Gauge(
            STATION_LED_BRIGHTNESS_METRIC_NAME,
            STATION_LED_BRIGHTNESS_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_rssi = Gauge(
            STATION_RSSI_METRIC_NAME,
            STATION_RSSI_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_uptime = Gauge(
            STATION_UPTIME_METRIC_NAME,
            STATION_UPTIME_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_pa_latency = Gauge(
            STATION_PA_LATENCY_METRIC_NAME,
            STATION_PA_LATENCY_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_memory = Gauge(
            STATION_MEMORY_METRIC_NAME,
            STATION_MEMORY_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_last_seen = Gauge(
            STATION_LAST_SEEN_METRIC_NAME,
            STATION_LAST_SEEN_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_last_modified = Gauge(
            STATION_LAST_MODIFIED_METRIC_NAME,
            STATION_LAST_MODIFIED_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_date_created = Gauge(
            STATION_DATE_CREATED_METRIC_NAME,
            STATION_DATE_CREATED_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_channel_state = Gauge(
            STATION_CHANNEL_STATE_METRIC_NAME,
            STATION_CHANNEL_STATE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_channel_flags = Gauge(
            STATION_CHANNEL_FLAGS_METRIC_NAME,
            STATION_CHANNEL_FLAGS_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_channel_flags_manual = Gauge(
            STATION_CHANNEL_FLAGS_MANUAL_METRIC_NAME,
            STATION_CHANNEL_FLAGS_MANUAL_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_channel_flags_auto = Gauge(
            STATION_CHANNEL_FLAGS_AUTO_METRIC_NAME,
            STATION_CHANNEL_FLAGS_AUTO_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_confidence = Gauge(
            STATION_CONFIDENCE_METRIC_NAME,
            STATION_CONFIDENCE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_confidence_manual = Gauge(
            STATION_CONFIDENCE_MANUAL_METRIC_NAME,
            STATION_CONFIDENCE_MANUAL_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._station_confidence_auto = Gauge(
            STATION_CONFIDENCE_AUTO_METRIC_NAME,
            STATION_CONFIDENCE_AUTO_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )

        # ---- Environmental fields ----
        self._environmental_humidity = Gauge(
            ENVIRONMENTAL_HUMIDITY_METRIC_NAME,
            ENVIRONMENTAL_HUMIDITY_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._environmental_humidity_a = Gauge(
            ENVIRONMENTAL_HUMIDITY_A_METRIC_NAME,
            ENVIRONMENTAL_HUMIDITY_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._environmental_humidity_b = Gauge(
            ENVIRONMENTAL_HUMIDITY_B_METRIC_NAME,
            ENVIRONMENTAL_HUMIDITY_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._environmental_temperature = Gauge(
            ENVIRONMENTAL_TEMPERATURE_METRIC_NAME,
            ENVIRONMENTAL_TEMPERATURE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._environmental_temperature_a = Gauge(
            ENVIRONMENTAL_TEMPERATURE_A_METRIC_NAME,
            ENVIRONMENTAL_TEMPERATURE_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._environmental_temperature_b = Gauge(
            ENVIRONMENTAL_TEMPERATURE_B_METRIC_NAME,
            ENVIRONMENTAL_TEMPERATURE_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._environmental_pressure = Gauge(
            ENVIRONMENTAL_PRESSURE_METRIC_NAME,
            ENVIRONMENTAL_PRESSURE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._environmental_pressure_a = Gauge(
            ENVIRONMENTAL_PRESSURE_A_METRIC_NAME,
            ENVIRONMENTAL_PRESSURE_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._environmental_pressure_b = Gauge(
            ENVIRONMENTAL_PRESSURE_B_METRIC_NAME,
            ENVIRONMENTAL_PRESSURE_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )

        # ---- Miscellaneous fields ----
        self._miscellaneous_voc = Gauge(
            MISCELLANEOUS_VOC_METRIC_NAME,
            MISCELLANEOUS_VOC_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._miscellaneous_voc_a = Gauge(
            MISCELLANEOUS_VOC_A_METRIC_NAME,
            MISCELLANEOUS_VOC_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._miscellaneous_voc_b = Gauge(
            MISCELLANEOUS_VOC_B_METRIC_NAME,
            MISCELLANEOUS_VOC_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._miscellaneous_ozone1 = Gauge(
            MISCELLANEOUS_OZONE1_METRIC_NAME,
            MISCELLANEOUS_OZONE1_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._miscellaneous_analog_input = Gauge(
            MISCELLANEOUS_ANALOG_INPUT_METRIC_NAME,
            MISCELLANEOUS_ANALOG_INPUT_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )

        # ---- PM1.0 fields ----
        self._pm1_0 = Gauge(
            PM1_0_METRIC_NAME,
            PM1_0_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm1_0_a = Gauge(
            PM1_0_A_METRIC_NAME,
            PM1_0_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm1_0_b = Gauge(
            PM1_0_B_METRIC_NAME,
            PM1_0_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm1_0_atm = Gauge(
            PM1_0_ATM_METRIC_NAME,
            PM1_0_ATM_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm1_0_atm_a = Gauge(
            PM1_0_ATM_A_METRIC_NAME,
            PM1_0_ATM_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm1_0_atm_b = Gauge(
            PM1_0_ATM_B_METRIC_NAME,
            PM1_0_ATM_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm1_0_cf_1 = Gauge(
            PM1_0_CF_1_METRIC_NAME,
            PM1_0_CF_1_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm1_0_cf_1_a = Gauge(
            PM1_0_CF_1_A_METRIC_NAME,
            PM1_0_CF_1_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm1_0_cf_1_b = Gauge(
            PM1_0_CF_1_B_METRIC_NAME,
            PM1_0_CF_1_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )

        # ---- PM2.5 fields ----
        self._pm2_5_alt = Gauge(
            PM2_5_ALT_METRIC_NAME,
            PM2_5_ALT_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_alt_a = Gauge(
            PM2_5_ALT_A_METRIC_NAME,
            PM2_5_ALT_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_alt_b = Gauge(
            PM2_5_ALT_B_METRIC_NAME,
            PM2_5_ALT_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5 = Gauge(
            PM2_5_METRIC_NAME,
            PM2_5_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_a = Gauge(
            PM2_5_A_METRIC_NAME,
            PM2_5_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_b = Gauge(
            PM2_5_B_METRIC_NAME,
            PM2_5_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_atm = Gauge(
            PM2_5_ATM_METRIC_NAME,
            PM2_5_ATM_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_atm_a = Gauge(
            PM2_5_ATM_A_METRIC_NAME,
            PM2_5_ATM_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_atm_b = Gauge(
            PM2_5_ATM_B_METRIC_NAME,
            PM2_5_ATM_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_cf_1 = Gauge(
            PM2_5_CF_1_METRIC_NAME,
            PM2_5_CF_1_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_cf_1_a = Gauge(
            PM2_5_CF_1_A_METRIC_NAME,
            PM2_5_CF_1_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_cf_1_b = Gauge(
            PM2_5_CF_1_B_METRIC_NAME,
            PM2_5_CF_1_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )

        # ---- PM2.5 pseudo average fields ----
        self._pm2_5_10minute = Gauge(
            PM2_5_10MINUTE_METRIC_NAME,
            PM2_5_10MINUTE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_10minute_a = Gauge(
            PM2_5_10MINUTE_A_METRIC_NAME,
            PM2_5_10MINUTE_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_10minute_b = Gauge(
            PM2_5_10MINUTE_B_METRIC_NAME,
            PM2_5_10MINUTE_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_30minute = Gauge(
            PM2_5_30MINUTE_METRIC_NAME,
            PM2_5_30MINUTE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_30minute_a = Gauge(
            PM2_5_30MINUTE_A_METRIC_NAME,
            PM2_5_30MINUTE_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_30minute_b = Gauge(
            PM2_5_30MINUTE_B_METRIC_NAME,
            PM2_5_30MINUTE_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_60minute = Gauge(
            PM2_5_60MINUTE_METRIC_NAME,
            PM2_5_60MINUTE_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_60minute_a = Gauge(
            PM2_5_60MINUTE_A_METRIC_NAME,
            PM2_5_60MINUTE_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_60minute_b = Gauge(
            PM2_5_60MINUTE_B_METRIC_NAME,
            PM2_5_60MINUTE_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_6hour = Gauge(
            PM2_5_6HOUR_METRIC_NAME,
            PM2_5_6HOUR_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_6hour_a = Gauge(
            PM2_5_6HOUR_A_METRIC_NAME,
            PM2_5_6HOUR_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_6hour_b = Gauge(
            PM2_5_6HOUR_B_METRIC_NAME,
            PM2_5_6HOUR_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_24hour = Gauge(
            PM2_5_24HOUR_METRIC_NAME,
            PM2_5_24HOUR_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_24hour_a = Gauge(
            PM2_5_24HOUR_A_METRIC_NAME,
            PM2_5_24HOUR_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_24hour_b = Gauge(
            PM2_5_24HOUR_B_METRIC_NAME,
            PM2_5_24HOUR_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_1week = Gauge(
            PM2_5_1WEEK_METRIC_NAME,
            PM2_5_1WEEK_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_1week_a = Gauge(
            PM2_5_1WEEK_A_METRIC_NAME,
            PM2_5_1WEEK_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm2_5_1week_b = Gauge(
            PM2_5_1WEEK_B_METRIC_NAME,
            PM2_5_1WEEK_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )

        # ---- PM10.0 fields ----
        self._pm10_0 = Gauge(
            PM10_0_METRIC_NAME,
            PM10_0_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm10_0_a = Gauge(
            PM10_0_A_METRIC_NAME,
            PM10_0_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm10_0_b = Gauge(
            PM10_0_B_METRIC_NAME,
            PM10_0_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm10_0_atm = Gauge(
            PM10_0_ATM_METRIC_NAME,
            PM10_0_ATM_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm10_0_atm_a = Gauge(
            PM10_0_ATM_A_METRIC_NAME,
            PM10_0_ATM_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm10_0_atm_b = Gauge(
            PM10_0_ATM_B_METRIC_NAME,
            PM10_0_ATM_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm10_0_cf_1 = Gauge(
            PM10_0_CF_1_METRIC_NAME,
            PM10_0_CF_1_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm10_0_cf_1_a = Gauge(
            PM10_0_CF_1_A_METRIC_NAME,
            PM10_0_CF_1_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._pm10_0_cf_1_b = Gauge(
            PM10_0_CF_1_B_METRIC_NAME,
            PM10_0_CF_1_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )

        # ---- Particle count fields ----
        self._um_count_0_3 = Gauge(
            UM_COUNT_0_3_METRIC_NAME,
            UM_COUNT_0_3_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_0_3_a = Gauge(
            UM_COUNT_0_3_A_METRIC_NAME,
            UM_COUNT_0_3_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_0_3_b = Gauge(
            UM_COUNT_0_3_B_METRIC_NAME,
            UM_COUNT_0_3_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_0_5 = Gauge(
            UM_COUNT_0_5_METRIC_NAME,
            UM_COUNT_0_5_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_0_5_a = Gauge(
            UM_COUNT_0_5_A_METRIC_NAME,
            UM_COUNT_0_5_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_0_5_b = Gauge(
            UM_COUNT_0_5_B_METRIC_NAME,
            UM_COUNT_0_5_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_1_0 = Gauge(
            UM_COUNT_1_0_METRIC_NAME,
            UM_COUNT_1_0_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_1_0_a = Gauge(
            UM_COUNT_1_0_A_METRIC_NAME,
            UM_COUNT_1_0_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_1_0_b = Gauge(
            UM_COUNT_1_0_B_METRIC_NAME,
            UM_COUNT_1_0_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_2_5 = Gauge(
            UM_COUNT_2_5_METRIC_NAME,
            UM_COUNT_2_5_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_2_5_a = Gauge(
            UM_COUNT_2_5_A_METRIC_NAME,
            UM_COUNT_2_5_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_2_5_b = Gauge(
            UM_COUNT_2_5_B_METRIC_NAME,
            UM_COUNT_2_5_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_5_0 = Gauge(
            UM_COUNT_5_0_METRIC_NAME,
            UM_COUNT_5_0_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_5_0_a = Gauge(
            UM_COUNT_5_0_A_METRIC_NAME,
            UM_COUNT_5_0_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_5_0_b = Gauge(
            UM_COUNT_5_0_B_METRIC_NAME,
            UM_COUNT_5_0_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_10_0 = Gauge(
            UM_COUNT_10_0_METRIC_NAME,
            UM_COUNT_10_0_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_10_0_a = Gauge(
            UM_COUNT_10_0_A_METRIC_NAME,
            UM_COUNT_10_0_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._um_count_10_0_b = Gauge(
            UM_COUNT_10_0_B_METRIC_NAME,
            UM_COUNT_10_0_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )

        # ---- ThingSpeak fields ----
        self._thingspeak_primary_id_a = Gauge(
            THINGSPEAK_PRIMARY_ID_A_METRIC_NAME,
            THINGSPEAK_PRIMARY_ID_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._thingspeak_secondary_id_a = Gauge(
            THINGSPEAK_SECONDARY_ID_A_METRIC_NAME,
            THINGSPEAK_SECONDARY_ID_A_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._thingspeak_primary_id_b = Gauge(
            THINGSPEAK_PRIMARY_ID_B_METRIC_NAME,
            THINGSPEAK_PRIMARY_ID_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )
        self._thingspeak_secondary_id_b = Gauge(
            THINGSPEAK_SECONDARY_ID_B_METRIC_NAME,
            THINGSPEAK_SECONDARY_ID_B_METRIC_DESCRIPTION,
            ["sensor_index"],
            registry=self._registry,
        )

        # Start the Prometheus HTTP server so metrics can be scraped
        start_http_server(self._prometheus_port, registry=self._registry)

    @staticmethod
    def _safe_numeric(value):
        """
        Convert a value to float for use with Prometheus Gauges.
        Returns NaN when the value is None or cannot be converted.

        :param value: The value to convert.
        :return: A float representation of the value, or NaN on failure.
        """

        if value is None:
            return float("nan")

        try:
            return float(value)

        except (TypeError, ValueError):
            return float("nan")

    def store_sensor_data(self, single_sensor_data_dict):
        """
        Update Prometheus Gauges with the latest sensor data.

        :param dict single_sensor_data_dict: A python dictionary containing all fields
                                             for insertion. If a sensor doesn't support
                                             a certain field make sure it is NULL and part
                                             of the dictionary. This method does no type
                                             or error checking. That is up to the caller.
        """

        sensor_index = str(single_sensor_data_dict["sensor_index"])

        # ---- Station information and status fields ----
        self._station_data_time_stamp.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["data_time_stamp"])
        )
        self._station_icon.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["icon"])
        )
        self._station_location_type.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["location_type"])
        )
        self._station_private.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["private"])
        )
        self._station_latitude.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["latitude"])
        )
        self._station_longitude.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["longitude"])
        )
        self._station_altitude.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["altitude"])
        )
        self._station_position_rating.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["position_rating"])
        )
        self._station_led_brightness.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["led_brightness"])
        )
        self._station_rssi.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["rssi"])
        )
        self._station_uptime.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["uptime"])
        )
        self._station_pa_latency.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pa_latency"])
        )
        self._station_memory.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["memory"])
        )
        self._station_last_seen.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["last_seen"])
        )
        self._station_last_modified.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["last_modified"])
        )
        self._station_date_created.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["date_created"])
        )
        self._station_channel_state.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["channel_state"])
        )
        self._station_channel_flags.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["channel_flags"])
        )
        self._station_channel_flags_manual.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["channel_flags_manual"])
        )
        self._station_channel_flags_auto.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["channel_flags_auto"])
        )
        self._station_confidence.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["confidence"])
        )
        self._station_confidence_manual.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["confidence_manual"])
        )
        self._station_confidence_auto.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["confidence_auto"])
        )

        # ---- Environmental fields ----
        self._environmental_humidity.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["humidity"])
        )
        self._environmental_humidity_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["humidity_a"])
        )
        self._environmental_humidity_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["humidity_b"])
        )
        self._environmental_temperature.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["temperature"])
        )
        self._environmental_temperature_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["temperature_a"])
        )
        self._environmental_temperature_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["temperature_b"])
        )
        self._environmental_pressure.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pressure"])
        )
        self._environmental_pressure_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pressure_a"])
        )
        self._environmental_pressure_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pressure_b"])
        )

        # ---- Miscellaneous fields ----
        self._miscellaneous_voc.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["voc"])
        )
        self._miscellaneous_voc_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["voc_a"])
        )
        self._miscellaneous_voc_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["voc_b"])
        )
        self._miscellaneous_ozone1.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["ozone1"])
        )
        self._miscellaneous_analog_input.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["analog_input"])
        )

        # ---- PM1.0 fields ----
        self._pm1_0.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm1.0"])
        )
        self._pm1_0_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm1.0_a"])
        )
        self._pm1_0_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm1.0_b"])
        )
        self._pm1_0_atm.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm1.0_atm"])
        )
        self._pm1_0_atm_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm1.0_atm_a"])
        )
        self._pm1_0_atm_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm1.0_atm_b"])
        )
        self._pm1_0_cf_1.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm1.0_cf_1"])
        )
        self._pm1_0_cf_1_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm1.0_cf_1_a"])
        )
        self._pm1_0_cf_1_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm1.0_cf_1_b"])
        )

        # ---- PM2.5 fields ----
        self._pm2_5_alt.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_alt"])
        )
        self._pm2_5_alt_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_alt_a"])
        )
        self._pm2_5_alt_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_alt_b"])
        )
        self._pm2_5.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5"])
        )
        self._pm2_5_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_a"])
        )
        self._pm2_5_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_b"])
        )
        self._pm2_5_atm.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_atm"])
        )
        self._pm2_5_atm_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_atm_a"])
        )
        self._pm2_5_atm_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_atm_b"])
        )
        self._pm2_5_cf_1.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_cf_1"])
        )
        self._pm2_5_cf_1_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_cf_1_a"])
        )
        self._pm2_5_cf_1_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_cf_1_b"])
        )

        # ---- PM2.5 pseudo average fields ----
        self._pm2_5_10minute.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_10minute"])
        )
        self._pm2_5_10minute_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_10minute_a"])
        )
        self._pm2_5_10minute_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_10minute_b"])
        )
        self._pm2_5_30minute.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_30minute"])
        )
        self._pm2_5_30minute_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_30minute_a"])
        )
        self._pm2_5_30minute_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_30minute_b"])
        )
        self._pm2_5_60minute.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_60minute"])
        )
        self._pm2_5_60minute_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_60minute_a"])
        )
        self._pm2_5_60minute_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_60minute_b"])
        )
        self._pm2_5_6hour.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_6hour"])
        )
        self._pm2_5_6hour_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_6hour_a"])
        )
        self._pm2_5_6hour_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_6hour_b"])
        )
        self._pm2_5_24hour.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_24hour"])
        )
        self._pm2_5_24hour_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_24hour_a"])
        )
        self._pm2_5_24hour_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_24hour_b"])
        )
        self._pm2_5_1week.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_1week"])
        )
        self._pm2_5_1week_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_1week_a"])
        )
        self._pm2_5_1week_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm2.5_1week_b"])
        )

        # ---- PM10.0 fields ----
        self._pm10_0.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm10.0"])
        )
        self._pm10_0_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm10.0_a"])
        )
        self._pm10_0_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm10.0_b"])
        )
        self._pm10_0_atm.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm10.0_atm"])
        )
        self._pm10_0_atm_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm10.0_atm_a"])
        )
        self._pm10_0_atm_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm10.0_atm_b"])
        )
        self._pm10_0_cf_1.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm10.0_cf_1"])
        )
        self._pm10_0_cf_1_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm10.0_cf_1_a"])
        )
        self._pm10_0_cf_1_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["pm10.0_cf_1_b"])
        )

        # ---- Particle count fields ----
        self._um_count_0_3.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["0.3_um_count"])
        )
        self._um_count_0_3_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["0.3_um_count_a"])
        )
        self._um_count_0_3_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["0.3_um_count_b"])
        )
        self._um_count_0_5.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["0.5_um_count"])
        )
        self._um_count_0_5_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["0.5_um_count_a"])
        )
        self._um_count_0_5_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["0.5_um_count_b"])
        )
        self._um_count_1_0.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["1.0_um_count"])
        )
        self._um_count_1_0_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["1.0_um_count_a"])
        )
        self._um_count_1_0_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["1.0_um_count_b"])
        )
        self._um_count_2_5.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["2.5_um_count"])
        )
        self._um_count_2_5_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["2.5_um_count_a"])
        )
        self._um_count_2_5_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["2.5_um_count_b"])
        )
        self._um_count_5_0.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["5.0_um_count"])
        )
        self._um_count_5_0_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["5.0_um_count_a"])
        )
        self._um_count_5_0_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["5.0_um_count_b"])
        )
        self._um_count_10_0.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["10.0_um_count"])
        )
        self._um_count_10_0_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["10.0_um_count_a"])
        )
        self._um_count_10_0_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["10.0_um_count_b"])
        )

        # ---- ThingSpeak fields ----
        self._thingspeak_primary_id_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["primary_id_a"])
        )
        self._thingspeak_secondary_id_a.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["secondary_id_a"])
        )
        self._thingspeak_primary_id_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["primary_id_b"])
        )
        self._thingspeak_secondary_id_b.labels(sensor_index=sensor_index).set(
            self._safe_numeric(single_sensor_data_dict["secondary_id_b"])
        )


if __name__ == "__main__":
    parser = generate_common_arg_parser(
        "Collect data from PurpleAir sensors and expose it as Prometheus metrics!"
    )

    parser.add_argument(
        "-prometheus_port",
        required=False,
        default=PROMETHEUS_DATA_LOGGER_DEFAULT_PORT,
        dest="prometheus_port",
        type=int,
        help="""The port number the Prometheus HTTP metrics endpoint will listen on.
                Defaults to {}.""".format(PROMETHEUS_DATA_LOGGER_DEFAULT_PORT),
    )

    args = parser.parse_args()

    # Make an instance of our data logger
    the_paa_prometheus_data_logger = PurpleAirPrometheusDataLogger(
        args.paa_read_key,
        args.paa_write_key,
        prometheus_port=args.prometheus_port,
    )

    # Choose what run method to execute depending on
    # paa_multiple_sensor_request_json_file/paa_single_sensor_request_json_file/paa_group_sensor_request_json_file/paa_local_sensor_request_json_file
    the_paa_prometheus_data_logger.validate_parameters_and_run(
        args.paa_multiple_sensor_request_json_file,
        args.paa_single_sensor_request_json_file,
        args.paa_group_sensor_request_json_file,
        args.paa_local_sensor_request_json_file,
    )
