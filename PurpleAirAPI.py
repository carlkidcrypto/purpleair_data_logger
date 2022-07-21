#!/usr/bin/env python3

"""
    A python3 class designed to fetch data from Purple Air's new API.
    https://api.purpleair.com/#api-welcome
"""

# Python Built In Libs
import requests
import json

PRINT_DEBUG_MSGS = True


def debug_log(debug_msg_string):
    """
        A helper function to print out
        debug messages only if DEBUG is defined
    """

    if PRINT_DEBUG_MSGS:
        print(debug_msg_string)


class PurpleAirAPI():
    """
        The PurpleAirAPI class to send only read requests
    """

    def __init__(self, your_api_read_key):

        # Save off the API key for interal usage
        self.__your_api_read_key = your_api_read_key

        # Create the base API request string. Must be HTTPS.
        self.__base_api_request_string = "https://api.purpleair.com/v1/"

        # Place holders for information we care about
        self.__api_version = ""
        self.__api_key_last_checked = 0
        self.__api_key_type = ""

        self.__check_an_api_key()

    def __check_an_api_key(self):
        """
            A method to check if an API key is valid.
        """
        request_url = self.__base_api_request_string + "keys"
        my_request = requests.get(request_url, headers={
                                  "X-API-Key": str(self.__your_api_read_key)})

        if my_request.status_code == 201:
            # We good :) get the request text
            the_request_text_as_json = json.loads(my_request.text)
            debug_log(the_request_text_as_json)
            self.__api_version = the_request_text_as_json["api_version"]
            self.__api_key_last_checked = the_request_text_as_json["time_stamp"]
            self.__api_key_type = the_request_text_as_json["api_key_type"]
            my_request.close()
            del my_request
            return True

        else:
            raise ValueError(
                f"Invalid API Key provided: {self.__your_api_read_key}")

    def recheck_api_key(self):
        """
            A method to recheck the API Key provided.
        """

        return self.__check_an_api_key()

    @property
    def get_api_version(self):
        """
            A method to return the API version being used.
        """

        return self.__api_version

    @property
    def get_api_key_last_checked(self):
        """
            A method to return the timestamp of when the API Key was last checked.
        """

        return self.__api_key_last_checked

    @property
    def get_api_key_type(self):
        """
            A method to return the API version being used.
        """

        return self.__api_key_type

    def get_sensor_data(self, sensor_index, read_key=None, fields=None):
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
        """

        request_url = self.__base_api_request_string + \
            "sensors/" + f"{sensor_index}"

        # Add to the request_url string depending on what optional parameters are
        # passed in
        if read_key and fields:
            request_url = request_url + \
                f"?read_key={str(read_key)}&fields={str(fields)}"

        elif not read_key and fields:
            request_url = request_url + f"?fields={str(fields)}"

        elif read_key and not fields:
            request_url = request_url + f"?read_key={str(read_key)}"

        my_request = requests.get(request_url, headers={
                                  "X-API-Key": str(self.__your_api_read_key)})

        if my_request.status_code == 200:
            # We good :) get the request text
            the_request_text_as_json = json.loads(my_request.text)
            debug_log(the_request_text_as_json)
            my_request.close()
            del my_request
            return the_request_text_as_json

        elif my_request.status_code == 400:
            the_request_text_as_json = json.loads(my_request.text)
            debug_log(the_request_text_as_json)
            my_request.close()
            raise ValueError(
                f"{the_request_text_as_json['error']} - {the_request_text_as_json['description']}")
