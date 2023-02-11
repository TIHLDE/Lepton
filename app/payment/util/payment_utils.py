from datetime import datetime

from django.conf import settings

import jwt
import requests

TOKEN_URL = "https://apitest.vipps.no/accessToken/get"
TOKEN_HEADERS = {
    "client_id": settings.VIPPS_CLIENT_ID,
    "client_secret": settings.VIPPS_CLIENT_SECRET,
    "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
    "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
    "Vipps-System-Name": settings.VIPPS_SYSTEM_NAME,
    "Vipps-System-Version": settings.VIPPS_SYSTEM_VERSION,
    "Vipps-System-Plugin-Name": settings.VIPPS_SYSTEM_PLUGIN_NAME,
    "Vipps-System-Plugin-Version": settings.VIPPS_SYSTEM_PLUGIN_VERSION,
    "Cookie": "fpc=AqiUsXVZL3NFr4JO1-F_-NRQ2zIJAQAAAEukedsOAAAA; stsservicecookie=estsfd; x-ms-gateway-slice=estsfd",
}


def get_new_access_token():
    response = requests.post(TOKEN_URL, headers=TOKEN_HEADERS).json()
    # TODO: Remove this print statement
    print(response)
    return (response["expires_on"], response["access_token"])
