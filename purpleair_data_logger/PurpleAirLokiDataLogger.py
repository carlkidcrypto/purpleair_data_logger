#!/usr/bin/env python3

"""
Copyright 2023 carlkidcrypto, All rights reserved.
A python class designed to use the PurpleAirAPI for requesting sensor(s) data.
Data will be pushed to a Grafana Loki instance via the Loki HTTP push API.

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

import json
import requests


class PurpleAirLokiDataLogger(PurpleAirDataLogger):
    """
    A data logger class that pushes PurpleAir sensor data to a Grafana Loki instance
    via the Loki HTTP push API. Grafana can then be used to visualize the stored data.
    """

    def __init__(
        self,
        PurpleAirApiReadKey=None,
        PurpleAirApiWriteKey=None,
        PurpleAirApiIpv4Address=None,
        loki_url=None,
        loki_usr=None,
        loki_pwd=None,
    ):
        """
        :param str PurpleAirApiReadKey: A valid PurpleAirAPI Read key
        :param str PurpleAirApiWriteKey: A valid PurpleAirAPI Write key
        :param list PurpleAirApiIpv4Address: A list of valid IPv4 string addresses with no CIDR's.
        :param str loki_url: The base URL of the Loki instance (e.g. 'http://localhost:3100').
        :param str loki_usr: Optional username for Loki basic authentication.
        :param str loki_pwd: Optional password for Loki basic authentication.
        """

        # Inherit everything from the parent base class: PurpleAirDataLogger
        super().__init__(
            PurpleAirApiReadKey, PurpleAirApiWriteKey, PurpleAirApiIpv4Address
        )

        # Save off the Loki connection details internally for later access
        self._loki_url = loki_url.rstrip("/") + "/loki/api/v1/push"
        self._loki_usr = loki_usr
        self._loki_pwd = loki_pwd

        # Init an error counter
        self._data_error_counter = 0

    def _push_to_loki(self, streams):
        """
        Send a list of log streams to the Loki push API endpoint.

        :param list streams: A list of Loki stream dicts, each containing 'stream' (labels dict)
                             and 'values' (list of [nanosecond_timestamp_str, log_line_str] pairs).
        """

        payload = {"streams": streams}

        auth = None
        if self._loki_usr is not None and self._loki_pwd is not None:
            auth = (self._loki_usr, self._loki_pwd)

        response = requests.post(
            self._loki_url,
            json=payload,
            auth=auth,
            timeout=10,
        )
        response.raise_for_status()

    def store_sensor_data(self, single_sensor_data_dict):
        """
        Push the sensor data to Loki. Each data group is sent as a separate Loki log stream
        labelled with 'sensor_index' and 'data_group'. The log line is a JSON string of the
        relevant fields for that group.

        :param dict single_sensor_data_dict: A python dictionary containing all fields
                                             for insertion. If a sensor doesn't support
                                             a certain field make sure it is NULL and part
                                             of the dictionary. This method does no type
                                             or error checking. That is up to the caller.
        """

        try:
            # Loki expects nanosecond-precision unix timestamps as strings.
            # data_time_stamp is a unix epoch value in seconds.
            ts_ns = str(int(single_sensor_data_dict["data_time_stamp"]) * 1_000_000_000)
            sensor_index = str(single_sensor_data_dict["sensor_index"])

            streams = [
                {
                    "stream": {
                        "sensor_index": sensor_index,
                        "data_group": "station_information_and_status_fields",
                    },
                    "values": [
                        [
                            ts_ns,
                            json.dumps(
                                {
                                    "data_time_stamp": single_sensor_data_dict[
                                        "data_time_stamp"
                                    ],
                                    "sensor_index": single_sensor_data_dict[
                                        "sensor_index"
                                    ],
                                    "name": single_sensor_data_dict["name"],
                                    "icon": single_sensor_data_dict["icon"],
                                    "model": single_sensor_data_dict["model"],
                                    "hardware": single_sensor_data_dict["hardware"],
                                    "location_type": single_sensor_data_dict[
                                        "location_type"
                                    ],
                                    "private": single_sensor_data_dict["private"],
                                    "latitude": single_sensor_data_dict["latitude"],
                                    "longitude": single_sensor_data_dict["longitude"],
                                    "altitude": single_sensor_data_dict["altitude"],
                                    "position_rating": single_sensor_data_dict[
                                        "position_rating"
                                    ],
                                    "led_brightness": single_sensor_data_dict[
                                        "led_brightness"
                                    ],
                                    "firmware_version": single_sensor_data_dict[
                                        "firmware_version"
                                    ],
                                    "firmware_upgrade": single_sensor_data_dict[
                                        "firmware_upgrade"
                                    ],
                                    "rssi": single_sensor_data_dict["rssi"],
                                    "uptime": single_sensor_data_dict["uptime"],
                                    "pa_latency": single_sensor_data_dict["pa_latency"],
                                    "memory": single_sensor_data_dict["memory"],
                                    "last_seen": single_sensor_data_dict["last_seen"],
                                    "last_modified": single_sensor_data_dict[
                                        "last_modified"
                                    ],
                                    "date_created": single_sensor_data_dict[
                                        "date_created"
                                    ],
                                    "channel_state": single_sensor_data_dict[
                                        "channel_state"
                                    ],
                                    "channel_flags": single_sensor_data_dict[
                                        "channel_flags"
                                    ],
                                    "channel_flags_manual": single_sensor_data_dict[
                                        "channel_flags_manual"
                                    ],
                                    "channel_flags_auto": single_sensor_data_dict[
                                        "channel_flags_auto"
                                    ],
                                    "confidence": single_sensor_data_dict["confidence"],
                                    "confidence_manual": single_sensor_data_dict[
                                        "confidence_manual"
                                    ],
                                    "confidence_auto": single_sensor_data_dict[
                                        "confidence_auto"
                                    ],
                                }
                            ),
                        ]
                    ],
                },
                {
                    "stream": {
                        "sensor_index": sensor_index,
                        "data_group": "environmental_fields",
                    },
                    "values": [
                        [
                            ts_ns,
                            json.dumps(
                                {
                                    "data_time_stamp": single_sensor_data_dict[
                                        "data_time_stamp"
                                    ],
                                    "sensor_index": single_sensor_data_dict[
                                        "sensor_index"
                                    ],
                                    "humidity": single_sensor_data_dict["humidity"],
                                    "humidity_a": single_sensor_data_dict["humidity_a"],
                                    "humidity_b": single_sensor_data_dict["humidity_b"],
                                    "temperature": single_sensor_data_dict["temperature"],
                                    "temperature_a": single_sensor_data_dict[
                                        "temperature_a"
                                    ],
                                    "temperature_b": single_sensor_data_dict[
                                        "temperature_b"
                                    ],
                                    "pressure": single_sensor_data_dict["pressure"],
                                    "pressure_a": single_sensor_data_dict["pressure_a"],
                                    "pressure_b": single_sensor_data_dict["pressure_b"],
                                }
                            ),
                        ]
                    ],
                },
                {
                    "stream": {
                        "sensor_index": sensor_index,
                        "data_group": "miscellaneous_fields",
                    },
                    "values": [
                        [
                            ts_ns,
                            json.dumps(
                                {
                                    "data_time_stamp": single_sensor_data_dict[
                                        "data_time_stamp"
                                    ],
                                    "sensor_index": single_sensor_data_dict[
                                        "sensor_index"
                                    ],
                                    "voc": single_sensor_data_dict["voc"],
                                    "voc_a": single_sensor_data_dict["voc_a"],
                                    "voc_b": single_sensor_data_dict["voc_b"],
                                    "ozone1": single_sensor_data_dict["ozone1"],
                                    "analog_input": single_sensor_data_dict[
                                        "analog_input"
                                    ],
                                }
                            ),
                        ]
                    ],
                },
                {
                    "stream": {
                        "sensor_index": sensor_index,
                        "data_group": "pm1_0_fields",
                    },
                    "values": [
                        [
                            ts_ns,
                            json.dumps(
                                {
                                    "data_time_stamp": single_sensor_data_dict[
                                        "data_time_stamp"
                                    ],
                                    "sensor_index": single_sensor_data_dict[
                                        "sensor_index"
                                    ],
                                    "pm1.0": single_sensor_data_dict["pm1.0"],
                                    "pm1.0_a": single_sensor_data_dict["pm1.0_a"],
                                    "pm1.0_b": single_sensor_data_dict["pm1.0_b"],
                                    "pm1.0_atm": single_sensor_data_dict["pm1.0_atm"],
                                    "pm1.0_atm_a": single_sensor_data_dict[
                                        "pm1.0_atm_a"
                                    ],
                                    "pm1.0_atm_b": single_sensor_data_dict[
                                        "pm1.0_atm_b"
                                    ],
                                    "pm1.0_cf_1": single_sensor_data_dict["pm1.0_cf_1"],
                                    "pm1.0_cf_1_a": single_sensor_data_dict[
                                        "pm1.0_cf_1_a"
                                    ],
                                    "pm1.0_cf_1_b": single_sensor_data_dict[
                                        "pm1.0_cf_1_b"
                                    ],
                                }
                            ),
                        ]
                    ],
                },
                {
                    "stream": {
                        "sensor_index": sensor_index,
                        "data_group": "pm2_5_fields",
                    },
                    "values": [
                        [
                            ts_ns,
                            json.dumps(
                                {
                                    "data_time_stamp": single_sensor_data_dict[
                                        "data_time_stamp"
                                    ],
                                    "sensor_index": single_sensor_data_dict[
                                        "sensor_index"
                                    ],
                                    "pm2.5_alt": single_sensor_data_dict["pm2.5_alt"],
                                    "pm2.5_alt_a": single_sensor_data_dict[
                                        "pm2.5_alt_a"
                                    ],
                                    "pm2.5_alt_b": single_sensor_data_dict[
                                        "pm2.5_alt_b"
                                    ],
                                    "pm2.5": single_sensor_data_dict["pm2.5"],
                                    "pm2.5_a": single_sensor_data_dict["pm2.5_a"],
                                    "pm2.5_b": single_sensor_data_dict["pm2.5_b"],
                                    "pm2.5_atm": single_sensor_data_dict["pm2.5_atm"],
                                    "pm2.5_atm_a": single_sensor_data_dict[
                                        "pm2.5_atm_a"
                                    ],
                                    "pm2.5_atm_b": single_sensor_data_dict[
                                        "pm2.5_atm_b"
                                    ],
                                    "pm2.5_cf_1": single_sensor_data_dict["pm2.5_cf_1"],
                                    "pm2.5_cf_1_a": single_sensor_data_dict[
                                        "pm2.5_cf_1_a"
                                    ],
                                    "pm2.5_cf_1_b": single_sensor_data_dict[
                                        "pm2.5_cf_1_b"
                                    ],
                                }
                            ),
                        ]
                    ],
                },
                {
                    "stream": {
                        "sensor_index": sensor_index,
                        "data_group": "pm2_5_pseudo_average_fields",
                    },
                    "values": [
                        [
                            ts_ns,
                            json.dumps(
                                {
                                    "data_time_stamp": single_sensor_data_dict[
                                        "data_time_stamp"
                                    ],
                                    "sensor_index": single_sensor_data_dict[
                                        "sensor_index"
                                    ],
                                    "pm2.5_10minute": single_sensor_data_dict[
                                        "pm2.5_10minute"
                                    ],
                                    "pm2.5_10minute_a": single_sensor_data_dict[
                                        "pm2.5_10minute_a"
                                    ],
                                    "pm2.5_10minute_b": single_sensor_data_dict[
                                        "pm2.5_10minute_b"
                                    ],
                                    "pm2.5_30minute": single_sensor_data_dict[
                                        "pm2.5_30minute"
                                    ],
                                    "pm2.5_30minute_a": single_sensor_data_dict[
                                        "pm2.5_30minute_a"
                                    ],
                                    "pm2.5_30minute_b": single_sensor_data_dict[
                                        "pm2.5_30minute_b"
                                    ],
                                    "pm2.5_60minute": single_sensor_data_dict[
                                        "pm2.5_60minute"
                                    ],
                                    "pm2.5_60minute_a": single_sensor_data_dict[
                                        "pm2.5_60minute_a"
                                    ],
                                    "pm2.5_60minute_b": single_sensor_data_dict[
                                        "pm2.5_60minute_b"
                                    ],
                                    "pm2.5_6hour": single_sensor_data_dict[
                                        "pm2.5_6hour"
                                    ],
                                    "pm2.5_6hour_a": single_sensor_data_dict[
                                        "pm2.5_6hour_a"
                                    ],
                                    "pm2.5_6hour_b": single_sensor_data_dict[
                                        "pm2.5_6hour_b"
                                    ],
                                    "pm2.5_24hour": single_sensor_data_dict[
                                        "pm2.5_24hour"
                                    ],
                                    "pm2.5_24hour_a": single_sensor_data_dict[
                                        "pm2.5_24hour_a"
                                    ],
                                    "pm2.5_24hour_b": single_sensor_data_dict[
                                        "pm2.5_24hour_b"
                                    ],
                                    "pm2.5_1week": single_sensor_data_dict[
                                        "pm2.5_1week"
                                    ],
                                    "pm2.5_1week_a": single_sensor_data_dict[
                                        "pm2.5_1week_a"
                                    ],
                                    "pm2.5_1week_b": single_sensor_data_dict[
                                        "pm2.5_1week_b"
                                    ],
                                }
                            ),
                        ]
                    ],
                },
                {
                    "stream": {
                        "sensor_index": sensor_index,
                        "data_group": "pm10_0_fields",
                    },
                    "values": [
                        [
                            ts_ns,
                            json.dumps(
                                {
                                    "data_time_stamp": single_sensor_data_dict[
                                        "data_time_stamp"
                                    ],
                                    "sensor_index": single_sensor_data_dict[
                                        "sensor_index"
                                    ],
                                    "pm10.0": single_sensor_data_dict["pm10.0"],
                                    "pm10.0_a": single_sensor_data_dict["pm10.0_a"],
                                    "pm10.0_b": single_sensor_data_dict["pm10.0_b"],
                                    "pm10.0_atm": single_sensor_data_dict["pm10.0_atm"],
                                    "pm10.0_atm_a": single_sensor_data_dict[
                                        "pm10.0_atm_a"
                                    ],
                                    "pm10.0_atm_b": single_sensor_data_dict[
                                        "pm10.0_atm_b"
                                    ],
                                    "pm10.0_cf_1": single_sensor_data_dict[
                                        "pm10.0_cf_1"
                                    ],
                                    "pm10.0_cf_1_a": single_sensor_data_dict[
                                        "pm10.0_cf_1_a"
                                    ],
                                    "pm10.0_cf_1_b": single_sensor_data_dict[
                                        "pm10.0_cf_1_b"
                                    ],
                                }
                            ),
                        ]
                    ],
                },
                {
                    "stream": {
                        "sensor_index": sensor_index,
                        "data_group": "particle_count_fields",
                    },
                    "values": [
                        [
                            ts_ns,
                            json.dumps(
                                {
                                    "data_time_stamp": single_sensor_data_dict[
                                        "data_time_stamp"
                                    ],
                                    "sensor_index": single_sensor_data_dict[
                                        "sensor_index"
                                    ],
                                    "0.3_um_count": single_sensor_data_dict[
                                        "0.3_um_count"
                                    ],
                                    "0.3_um_count_a": single_sensor_data_dict[
                                        "0.3_um_count_a"
                                    ],
                                    "0.3_um_count_b": single_sensor_data_dict[
                                        "0.3_um_count_b"
                                    ],
                                    "0.5_um_count": single_sensor_data_dict[
                                        "0.5_um_count"
                                    ],
                                    "0.5_um_count_a": single_sensor_data_dict[
                                        "0.5_um_count_a"
                                    ],
                                    "0.5_um_count_b": single_sensor_data_dict[
                                        "0.5_um_count_b"
                                    ],
                                    "1.0_um_count": single_sensor_data_dict[
                                        "1.0_um_count"
                                    ],
                                    "1.0_um_count_a": single_sensor_data_dict[
                                        "1.0_um_count_a"
                                    ],
                                    "1.0_um_count_b": single_sensor_data_dict[
                                        "1.0_um_count_b"
                                    ],
                                    "2.5_um_count": single_sensor_data_dict[
                                        "2.5_um_count"
                                    ],
                                    "2.5_um_count_a": single_sensor_data_dict[
                                        "2.5_um_count_a"
                                    ],
                                    "2.5_um_count_b": single_sensor_data_dict[
                                        "2.5_um_count_b"
                                    ],
                                    "5.0_um_count": single_sensor_data_dict[
                                        "5.0_um_count"
                                    ],
                                    "5.0_um_count_a": single_sensor_data_dict[
                                        "5.0_um_count_a"
                                    ],
                                    "5.0_um_count_b": single_sensor_data_dict[
                                        "5.0_um_count_b"
                                    ],
                                    "10.0_um_count": single_sensor_data_dict[
                                        "10.0_um_count"
                                    ],
                                    "10.0_um_count_a": single_sensor_data_dict[
                                        "10.0_um_count_a"
                                    ],
                                    "10.0_um_count_b": single_sensor_data_dict[
                                        "10.0_um_count_b"
                                    ],
                                }
                            ),
                        ]
                    ],
                },
                {
                    "stream": {
                        "sensor_index": sensor_index,
                        "data_group": "thingspeak_fields",
                    },
                    "values": [
                        [
                            ts_ns,
                            json.dumps(
                                {
                                    "data_time_stamp": single_sensor_data_dict[
                                        "data_time_stamp"
                                    ],
                                    "sensor_index": single_sensor_data_dict[
                                        "sensor_index"
                                    ],
                                    "primary_id_a": single_sensor_data_dict[
                                        "primary_id_a"
                                    ],
                                    "primary_key_a": single_sensor_data_dict[
                                        "primary_key_a"
                                    ],
                                    "secondary_id_a": single_sensor_data_dict[
                                        "secondary_id_a"
                                    ],
                                    "secondary_key_a": single_sensor_data_dict[
                                        "secondary_key_a"
                                    ],
                                    "primary_id_b": single_sensor_data_dict[
                                        "primary_id_b"
                                    ],
                                    "primary_key_b": single_sensor_data_dict[
                                        "primary_key_b"
                                    ],
                                    "secondary_id_b": single_sensor_data_dict[
                                        "secondary_id_b"
                                    ],
                                    "secondary_key_b": single_sensor_data_dict[
                                        "secondary_key_b"
                                    ],
                                }
                            ),
                        ]
                    ],
                },
            ]

            self._push_to_loki(streams)

        except Exception as except_err:
            self._data_error_counter = self._data_error_counter + 1
            print("We weren't able to push the current data to Loki!")
            print(f"Data error counter is at {self._data_error_counter}")
            print(f"Error is {except_err} \n")

        # Delete some stuff
        del single_sensor_data_dict


if __name__ == "__main__":
    parser = generate_common_arg_parser(
        "Collect data from PurpleAir sensors and push it to a Grafana Loki instance!"
    )

    parser.add_argument(
        "-loki_url",
        required=True,
        dest="loki_url",
        type=str,
        help="""The base URL of the Loki instance (e.g. 'http://localhost:3100').""",
    )

    parser.add_argument(
        "-loki_usr",
        required=False,
        default=None,
        dest="loki_usr",
        type=str,
        help="""The Loki username for basic authentication.""",
    )

    parser.add_argument(
        "-loki_pwd",
        required=False,
        default=None,
        dest="loki_pwd",
        type=str,
        help="""The Loki password for basic authentication.""",
    )

    args = parser.parse_args()

    # Place holders that are used later down
    the_json_file = None
    file_obj = None

    # Second make an instance of our data logger
    ipv4_address_list = []
    if args.paa_local_sensor_request_json_file:
        import json as _json

        file_obj = open(args.paa_local_sensor_request_json_file, "r")
        the_json_file = _json.load(file_obj)
        file_obj.close()
        ipv4_address_list = the_json_file["sensor_ip_list"]
        del the_json_file

    the_paa_loki_data_logger = PurpleAirLokiDataLogger(
        args.paa_read_key,
        args.paa_write_key,
        ipv4_address_list,
        args.loki_url,
        args.loki_usr,
        args.loki_pwd,
    )

    # Third choose what run method to execute depending on
    # paa_multiple_sensor_request_json_file/paa_single_sensor_request_json_file/paa_group_sensor_request_json_file/paa_local_sensor_request_json_file
    the_paa_loki_data_logger.validate_parameters_and_run(
        args.paa_multiple_sensor_request_json_file,
        args.paa_single_sensor_request_json_file,
        args.paa_group_sensor_request_json_file,
        args.paa_local_sensor_request_json_file,
    )
