#!/usr/bin/env python3

"""
    A python3 class designed to fetch data from Purple Air's new API.
    https://api.purpleair.com/#api-welcome
"""

# Python Built In Libs
import requests
import json
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
        my_request = requests.get(request_url, headers={"X-API-Key": str(self.__your_api_read_key)})

        if my_request.status_code == 201:
            # We good :) get the request text
            the_request_text_as_json = json.loads(my_request.text)
            print(the_request_text_as_json)
            self.__api_version = the_request_text_as_json["api_version"]
            self.__api_key_last_checked = the_request_text_as_json["time_stamp"]
            self.__api_key_type = the_request_text_as_json["api_key_type"]
    
    @property
    def get_api_version(self):
        """
            A method to return the API version being used.
        """

        return self.__api_version

    @property
    def get_api_key_last_checked(self):
        """
            A method to return the API version being used.
        """

        return self.__api_key_last_checked
    
    @property
    def get_api_key_type(self):
        """
            A method to return the API version being used.
        """

        return self.__api_key_type

