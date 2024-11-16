import binascii
import os

from requests import PreparedRequest


def generate_otp():
    return binascii.hexlify(os.urandom(16)).decode()


def add_query_params(url, params):
    # type: (str, dict) -> str
    try:
        prepared_request = PreparedRequest()
        prepared_request.prepare_url(url, params)

        if prepared_request.url == None:
            return url

        return prepared_request.url
    except:
        return url
