#!/usr/bin/env python3

"""
    Copyright 2023 carlkidcrypto, All rights reserved.
    A python3 file containing mock helper functions for the PurpleAirAPIHelper file.
    https://api.purpleair.com/#api-welcome
"""

from purpleair_api.PurpleAirAPIHelpers import send_url_get_request as sugr
from purpleair_api.PurpleAirAPIHelpers import send_url_post_request as supr
from purpleair_api.PurpleAirAPIHelpers import send_url_delete_request as sudr
import requests_mock

FAKE_RETURN_STATUS_CODE = 200
FAKE_RETURN_TEXT = {}


def send_url_get_request(
    request_url,
    api_key_to_use=None,
    first_optional_parameter_separator=None,
    optional_parameters_dict=None,
):
    """
    This mocks out purpleair_api.PurpleAirAPIHelpers.send_url_get_request
    """

    with requests_mock.Mocker() as m:
        m.get(
            request_url,
            text=FAKE_RETURN_TEXT,
            status_code=FAKE_RETURN_STATUS_CODE,
        )
        sugr(
            request_url,
            api_key_to_use,
            first_optional_parameter_separator,
            optional_parameters_dict,
        )


def send_url_post_request(request_url, api_key_to_use, json_post_parameters={}):
    """
    This mocks out purpleair_api.PurpleAirAPIHelpers.send_url_post_request
    """

    with requests_mock.Mocker() as m:
        m.post(
            request_url,
            text=FAKE_RETURN_TEXT,
            status_code=FAKE_RETURN_STATUS_CODE,
        )
        supr(request_url, api_key_to_use, json_post_parameters)


def send_url_delete_request(request_url, api_key_to_use, json_post_parameters={}):
    """
    This mocks out purpleair_api.PurpleAirAPIHelpers.send_url_delete_request
    """

    with requests_mock.Mocker() as m:
        m.delete(
            request_url,
            text=FAKE_RETURN_TEXT,
            status_code=FAKE_RETURN_STATUS_CODE,
        )
        sudr(request_url, api_key_to_use, json_post_parameters)
