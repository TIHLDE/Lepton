import json

from django.conf import settings

import requests

# TODO : Try removing cookie from headers
TOKEN_URL = settings.VIPPS_TOKEN_URL
TOKEN_HEADERS = {
    "client_id": settings.VIPPS_CLIENT_ID,
    "client_secret": settings.VIPPS_CLIENT_SECRET,
    "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
    "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
    "Cookie": settings.VIPPS_COOKIE,
}


def get_new_access_token():
    response = requests.post(TOKEN_URL, headers=TOKEN_HEADERS).json()
    return (response["expires_on"], response["access_token"])


def initiate_payment(amount, order_id, event_name, access_token):
    """
    Initiate a payment with Vipps
    amount: Amount to pay in Øre (100 NOK = 10000)
    """
    url = settings.VIPPS_ORDER_URL
    payload = json.dumps(
        {
            "merchantInfo": {
                "callbackPrefix": settings.VIPPS_CALLBACK_PREFIX,
                "fallBack": settings.VIPPS_FALLBACK,
                "merchantSerialNumber": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
            },
            "transaction": {
                "amount": amount,
                "transactionText": "This payment is for the event:" + event_name,
                "orderId": order_id,
                "skipLandingPage": False,
            },
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
        "Authorization": "Bearer " + access_token,
        "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
        "Cookie": settings.VIPPS_COOKIE,
    }
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        raise Exception("Could not initiate payment")

    return response.json()
