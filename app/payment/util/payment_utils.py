import json
import os
from datetime import datetime

from django.conf import settings

import requests


def get_new_access_token():
    """
    Get new access token from Vipps for dealing with payments from Vipps.
    """
    TOKEN_URL = settings.VIPPS_TOKEN_URL
    TOKEN_HEADERS = {
        "client_id": settings.VIPPS_CLIENT_ID,
        "client_secret": settings.VIPPS_CLIENT_SECRET,
        "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
        "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
    }

    response = requests.post(TOKEN_URL, headers=TOKEN_HEADERS)

    if response.status_code != 200:
        raise Exception("Could not get access token")

    response = response.json()

    return response["expires_on"], response["access_token"]


def check_access_token():
    """
    Checks for access token.
    Updates acces token if expired.
    Returns new access token.
    """
    access_token = os.environ.get("PAYMENT_ACCESS_TOKEN")
    expires_at = os.environ.get("PAYMENT_ACCESS_TOKEN_EXPIRES_AT")

    if not access_token or datetime.now() >= datetime.fromtimestamp(int(expires_at)):
        (expires_at, access_token) = get_new_access_token()
        os.environ.update({"PAYMENT_ACCESS_TOKEN": access_token})
        os.environ.update({"PAYMENT_ACCESS_TOKEN_EXPIRES_AT": str(expires_at)})

    return access_token


def get_payment_order_status(order_id):
    """
    Returns status of payment order.
    """

    access_token = check_access_token()

    url = f"{settings.VIPPS_ORDER_URL}{order_id}/details"
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
        "Authorization": "Bearer " + access_token,
        "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
    }

    res = requests.get(url, headers=headers)
    json = res.json()

    return json["transactionLogHistory"][0]["operation"]


def initiate_payment(amount, order_id, access_token, transaction_text, fallback):
    """
    Initiate a payment with Vipps
    amount: Amount to pay in Øre (100 NOK = 10000)
    """
    url = settings.VIPPS_ORDER_URL
    payload = json.dumps(
        {
            "merchantInfo": {
                "callbackPrefix": settings.VIPPS_CALLBACK_PREFIX,
                "fallBack": f"{settings.VIPPS_FALLBACK}{fallback}",
                "merchantSerialNumber": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
            },
            "transaction": {
                "amount": amount,
                "transactionText": transaction_text,
                "orderId": order_id,
                "skipLandingPage": False,
                "scope": "name phoneNumber",
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


def refund_payment(amount, order_id, access_token, transaction_text):
    """
    Refund a payment from Vipps
    amount: Amount to pay in Øre (100 NOK = 10000)
    """

    url = f"{settings.VIPPS_ORDER_URL}/{order_id}/refund/"

    payload = json.dumps(
        {
            "merchantInfo": {
                "merchantSerialNumber": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
            },
            "transaction": {
                "amount": amount,
                "transactionText": transaction_text,
            },
        }
    )

    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
        "Authorization": "Bearer " + access_token,
        "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
        "X-Request-Id": order_id,
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        raise Exception("Could not refund payment")
