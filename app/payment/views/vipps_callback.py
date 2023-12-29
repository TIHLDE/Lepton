import json

from django.conf import settings
from django.http import HttpResponse

import requests

from app.payment.models.order import Order
from app.payment.util.payment_utils import get_new_access_token


def force_payment(order_id):
    """Force payment for an order."""
    access_token = get_new_access_token()[1]
    url = f"{settings.VIPPS_FORCE_PAYMENT_URL}{order_id}/approve"
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
        "Authorization": "Bearer " + access_token,
        "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
    }

    res = requests.post(url, headers=headers)
    status_code = res.status_code
    json = res.json()
    return (json, status_code)
