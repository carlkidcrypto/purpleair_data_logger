#!/usr/bin/env python3

"""
    Copyright 2022 carlkid1499, All rights reserved.
    A python3 class designed to fetch data from Purple Air's new API.
    https://api.purpleair.com/#api-welcome
"""

import requests
import json
from purpleair_data_logger.PurpleAirAPIConstants import (
    ACCEPTED_FIELD_NAMES_DICT, PRINT_DEBUG_MSGS, SUCCESS_CODE_LIST, ERROR_CODES_LIST)


class PurpleAirAPIError(Exception):
    """ 
        Custom Exception for our PurpleAirAPI class.
    """

    def __init__(self, message_string):
        self.message = message_string
        super().__init__(self.message)


def debug_log(debug_msg_string):
    """
        A helper function to print out
        debug messages only if DEBUG is defined as True in
        'PurpleAirAPIConstants.py'. Messages will be the color
        red.
    """

    if PRINT_DEBUG_MSGS:
        # Make debug messages red using ANSI escape code.
        print("\033[1;31m" + str(debug_msg_string) + "\x1b[0m")


class PurpleAirAPI():
    """
        The PurpleAirAPI class designed to send valid
        PurpleAirAPI requests.
    """

    def __init__(self, your_api_read_key):

        # Save off the API key for internal usage
        self._your_api_read_key = your_api_read_key

        # Create the base API request string. Must be HTTPS.
        self._base_api_request_string = "https://api.purpleair.com/v1/"

        # Place holders for information we care about
        self._api_version = ""
        self._api_key_last_checked = 0
        self._api_key_type = ""

        retval = self._check_an_api_key()
        if retval:
            print("Successfully authenticated with the PurpleAirAPI")

    def _check_an_api_key(self):
        """
            A method to check if an API key is valid.
        """
        request_url = self._base_api_request_string + "keys"
        my_request = requests.get(request_url, headers={
                                  "X-API-Key": str(self._your_api_read_key)})

        the_request_text_as_json = json.loads(my_request.text)
        debug_log(the_request_text_as_json)

        if my_request.status_code in SUCCESS_CODE_LIST:
            # We good :) get the request text
            self._api_version = the_request_text_as_json["api_version"]
            self._api_key_last_checked = the_request_text_as_json["time_stamp"]
            self._api_key_type = the_request_text_as_json["api_key_type"]
            my_request.close()
            del my_request
            return True

        else:
            raise PurpleAirAPIError(
                f"""{my_request.status_code}: {the_request_text_as_json['error']} - {the_request_text_as_json['description']}""")

    def recheck_api_key(self):
        """
            A method to recheck the API Key provided.
        """

        return self._check_an_api_key()

    @property
    def get_api_version(self):
        """
            A method to return the API version being used.
        """

        return self._api_version

    @property
    def get_api_key_last_checked(self):
        """
            A method to return the timestamp of when the API Key was last checked.
        """

        return self._api_key_last_checked

    @property
    def get_api_key_type(self):
        """
            A method to return the API version being used.
        """

        return self._api_key_type

    def request_sensor_data(self, sensor_index, read_key=None, fields=None):
        """
            A method to retrieve sensor data from one sensor. Will return the 
            response payload as a python dictionary.

            :param int sensor_index: The sensor_index as found in the JSON for
                                     this specific sensor.
    
            :param (optional) str read_key: This read_key is required for
                                            private devices. It is separate
                                            to the api_key and each sensor has
                                            its own read_key. Submit multiple
                                            keys by separating them with a
                                            comma (,) character for example:
                                            key-one,key-two,key-three.

            :param (optional) str fields: The 'Fields' parameter specifies which
                                          'sensor data fields' to include in the
                                          response. It is a comma separated list
                                          with one or more of the following:
                                          Refer to PurpleAir documentation for more
                                          information:
                                          https://api.purpleair.com/#api-sensors-get-sensor-data

            :return A python dictionary containing the payload response
        """

        request_url = self._base_api_request_string + \
            "sensors/" + f"{sensor_index}"

        optional_parameters_dict = {
            "read_key": read_key,
            "fields": fields
        }

        return self._send_url_request(request_url, optional_parameters_dict)

    def request_multiple_sensors_data(self, fields, location_type=None, read_keys=None, show_only=None, modified_since=None, max_age=None, nwlng=None, nwlat=None, selng=None, selat=None):
        """
            A method to retrieve sensor data from multiple sensors. Will return the 
            response payload as a python dictionary.

            :param str fields: The 'Fields' parameter specifies which 'sensor data fields' to include in the response. It is a comma separated list with one or more of the following:
                                Station information and status fields:
                                name, icon, model, hardware, location_type, private, latitude, longitude, altitude, position_rating, led_brightness, firmware_version, firmware_upgrade, rssi, uptime, pa_latency, memory, last_seen, last_modified, date_created, channel_state, channel_flags, channel_flags_manual, channel_flags_auto, confidence, confidence_manual, confidence_auto

                                Environmental fields:
                                humidity, humidity_a, humidity_b, temperature, temperature_a, temperature_b, pressure, pressure_a, pressure_b

                                Miscellaneous fields:
                                voc, voc_a, voc_b, ozone1, analog_input

                                PM1.0 fields:
                                pm1.0, pm1.0_a, pm1.0_b, pm1.0_atm, pm1.0_atm_a, pm1.0_atm_b, pm1.0_cf_1, pm1.0_cf_1_a, pm1.0_cf_1_b

                                PM2.5 fields:
                                pm2.5_alt, pm2.5_alt_a, pm2.5_alt_b, pm2.5, pm2.5_a, pm2.5_b, pm2.5_atm, pm2.5_atm_a, pm2.5_atm_b, pm2.5_cf_1, pm2.5_cf_1_a, pm2.5_cf_1_b

                                PM2.5 pseudo (simple running) average fields:
                                pm2.5_10minute, pm2.5_10minute_a, pm2.5_10minute_b, pm2.5_30minute, pm2.5_30minute_a, pm2.5_30minute_b, pm2.5_60minute, pm2.5_60minute_a, pm2.5_60minute_b, pm2.5_6hour, pm2.5_6hour_a, pm2.5_6hour_b, pm2.5_24hour, pm2.5_24hour_a, pm2.5_24hour_b, pm2.5_1week, pm2.5_1week_a, pm2.5_1week_b

                                PM10.0 fields:
                                pm10.0, pm10.0_a, pm10.0_b, pm10.0_atm, pm10.0_atm_a, pm10.0_atm_b, pm10.0_cf_1, pm10.0_cf_1_a, pm10.0_cf_1_b

                                Visibility fields:
                                scattering_coefficient, scattering_coefficient_a, scattering_coefficient_b, deciviews, deciviews_a, deciviews_b, visual_range, visual_range_a, visual_range_b

                                Particle count fields:
                                0.3_um_count, 0.3_um_count_a, 0.3_um_count_b, 0.5_um_count, 0.5_um_count_a, 0.5_um_count_b, 1.0_um_count, 1.0_um_count_a, 1.0_um_count_b, 2.5_um_count, 2.5_um_count_a, 2.5_um_count_b, 5.0_um_count, 5.0_um_count_a, 5.0_um_count_b, 10.0_um_count 10.0_um_count_a, 10.0_um_count_b

                                ThingSpeak fields, used to retrieve data from api.thingspeak.com:
                                primary_id_a, primary_key_a, secondary_id_a, secondary_key_a, primary_id_b, primary_key_b, secondary_id_b, secondary_key_b
                                
            :param (optional) int location_type: The location_type of the sensors.
                                                 Possible values are: 0 = Outside or 1 = Inside.

            :param (optional) str read_keys: A read_key is required for private devices. It is separate to the api_key and each sensor has its own read_key.
                                             Submit multiple keys by separating them with a comma (,) character for example: key-one,key-two,key-three
            
            :param (optional) str show_only: A comma (,) separated list of sensor_index values. When provided, the results are limited only to
                                             the sensors included in this list.

            :param (optional) str modified_since: The modified_since parameter causes only sensors modified after
                                                  the provided time stamp to be included in the results. Using the
                                                  time_stamp value from a previous call (recommended) will limit results
                                                  to those with new values since the last request. Using a value of 0
                                                  will match sensors modified at any time

            :param (optional) int max_age: Filter results to only include sensors modified or updated within the last
                                           number of seconds. Using a value of 0 will match sensors of any age. 
                                           Default value: 604800
            
            :param (optional) int nwlng: A north west longitude for the bounding box. Use a bounding box to limit the sensors
                                         returned to a specific geographic area. The bounding box is defined by two points, a
                                         north west latitude/longitude and a south east latitude/longitude.

            :param (optional) int nwlat: A north west latitude for the bounding box.

            :param (optional) int selng: A south east longitude for the bounding box.

            :param (optional) int selat: A south east latitude for the bounding box.

            :return A python dictionary containing the payload response                    
        """

        request_url = self._base_api_request_string + \
            "sensors/" + f"?fields={fields}"

        # Add to the request_url string depending on what optional parameters are
        # passed in. Turn them into a list of optional parameters
        optional_parameters_dict = {
            "location_type": location_type,
            "read_keys": read_keys,
            "show_only": show_only,
            "modified_since": modified_since,
            "max_age": max_age,
            "nwlng": nwlng,
            "nwlat": nwlat,
            "selng": selng,
            "selat": selat}

        return self._send_url_request(request_url, optional_parameters_dict)

    def request_sensor_historic_data(self, sensor_index, fields, read_key=None, start_timestamp=None, end_timestamp=None, average=None):
        """
            A method to request historic data from a single sensor.

            :param int sensor_index: The sensor_index as found in the JSON for this specific sensor.

            :param (optional) str read_key: This read_key is required for private devices. It is separate to the api_key and each sensor has its own read_key. Submit multiple keys by separating them with a comma (,) character for example: key-one,key-two,key-three.

            :param (optional) int start_timestamp: The time stamp of the first required history entry. Query is executed using data_timestamp >= start_timestamp.
                                                   Time can be specified as a UNIX time stamp in seconds or an ISO 8601 string. https://en.wikipedia.org/wiki/ISO_8601.
                                                   The time_stamp column in the resulting JSON or CSV will be in the same format and or time zone that you use for this start_timestamp parameter.
                                                   If not specified, the last maximum time span for the requested average will be returned.

            :param (optional) int end_timestamp: The end time stamp of the history to return. Query is executed using data_timestamp < end_timestamp.
                                                 Time can be specified as a UNIX time stamp in seconds or an ISO 8601 string. https://en.wikipedia.org/wiki/ISO_8601.
                                                 If not specified, the maximum time span will be returned starting from the provided start_timestamp.

            :param (optional) int average: The desired average in minutes, one of the following: 0 (real-time), 10 (default if not specified), 30, 60, 360 (6 hour), 1440 (1 day)
                                           Coming soon: 10080 (1 week), 44640 (1 month), 525600 (1 year).

            :param str fields: The 'Fields' parameter specifies which 'sensor data fields' to include in the response. Not all fields are available as history fields and we will be working to add more as time goes on. Fields marked with an asterisk (*) may not be available when using averages. It is a comma separated list with one or more of the following:

                               Station information and status fields:
                               hardware*, latitude*, longitude*, altitude*, firmware_version*, rssi, uptime, pa_latency, memory,

                               Environmental fields:
                               humidity, humidity_a, humidity_b, temperature, temperature_a, temperature_b, pressure, pressure_a, pressure_b

                               Miscellaneous fields:
                               voc, voc_a, voc_b, analog_input

                               PM1.0 fields:
                               pm1.0_atm, pm1.0_atm_a, pm1.0_atm_b, pm1.0_cf_1, pm1.0_cf_1_a, pm1.0_cf_1_b

                               PM2.5 fields:
                               pm2.5_alt, pm2.5_alt_a, pm2.5_alt_b, pm2.5_atm, pm2.5_atm_a, pm2.5_atm_b, pm2.5_cf_1, pm2.5_cf_1_a, pm2.5_cf_1_b

                               PM10.0 fields:
                               pm10.0_atm, pm10.0_atm_a, pm10.0_atm_b, pm10.0_cf_1, pm10.0_cf_1_a, pm10.0_cf_1_b

                               Visibility fields:
                               scattering_coefficient, scattering_coefficient_a, scattering_coefficient_b, deciviews, deciviews_a, deciviews_b, visual_range, visual_range_a, visual_range_b

                               Particle count fields:
                               0.3_um_count, 0.3_um_count_a, 0.3_um_count_b, 0.5_um_count, 0.5_um_count_a, 0.5_um_count_b, 1.0_um_count, 1.0_um_count_a, 1.0_um_count_b, 2.5_um_count, 2.5_um_count_a, 2.5_um_count_b, 5.0_um_count, 5.0_um_count_a, 5.0_um_count_b, 10.0_um_count, 10.0_um_count_a, 10.0_um_count_b

                               For field descriptions, please see the 'sensor data fields'. section.
        """

        request_url = self._base_api_request_string + \
            "sensors/" + f"{sensor_index}" + "/history" + f"?fields={fields}"

        # Add to the request_url string depending on what optional parameters are
        # passed in. Turn them into a list of optional parameters
        optional_parameters_dict = {
            "read_key": read_key,
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "modified_since": end_timestamp,
            "average": average}

        return self._send_url_request(request_url, optional_parameters_dict)

    def _send_url_request(self, request_url, optional_parameters_dict={}):
        """
            A class helper to send the url request. It can also add onto the
            'request_url' string if 'optional_parameters_dict' are provided.

            :param str request_url: The constructed string url request string.
            :param dict optional_parameters_dict: Optional parameters that can be added onto the
                                                  request_url. By default '{}'.
        """

        if optional_parameters_dict is not {}:
            opt_param_count = 0
            for opt_param, val in optional_parameters_dict.items():
                if val is not None:
                    opt_param_count = opt_param_count + 1

                    if opt_param_count == 1:
                        request_url = request_url + \
                            f"?{opt_param}={str(val)}"

                    elif opt_param_count >= 2:
                        request_url = request_url + \
                            f"&{opt_param}={str(val)}"

        debug_log(request_url)
        my_request = requests.get(request_url, headers={
                                  "X-API-Key": str(self._your_api_read_key)})

        the_request_text_as_json = json.loads(my_request.text)
        debug_log(the_request_text_as_json)

        if my_request.status_code in SUCCESS_CODE_LIST:
            my_request.close()
            del my_request
            return the_request_text_as_json

        elif my_request.status_code in ERROR_CODES_LIST:
            my_request.close()
            raise PurpleAirAPIError(
                f"""{my_request.status_code}: {the_request_text_as_json['error']} - {the_request_text_as_json['description']}""")

    def _sanitize_sensor_data_from_paa(self, paa_return_data):
        """
            A method for: Not all sensors support all field names, so we check that the keys exist
            in the sensor data. If not we add it in with a NULL equivalent. i.e 0.0, 0, "", etc.
            We access the "sensor" key inside this method.
        """

        for key_str in ACCEPTED_FIELD_NAMES_DICT.keys():
            if key_str not in paa_return_data["sensor"].keys():
                paa_return_data["sensor"][key_str] = ACCEPTED_FIELD_NAMES_DICT[key_str]

        return paa_return_data
