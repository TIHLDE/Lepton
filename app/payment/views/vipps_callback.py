import json

from django.conf import settings
from django.http import HttpResponse

import requests

from app.payment.models.order import Order
from app.payment.util.payment_utils import get_new_access_token


def vipps_callback(request, order_id):
    """Callback from vipps."""
    order = Order.objects.get(order_id=order_id)
    body = request.body
    data = json.loads(body)

    MSN = data["merchantSerialNumber"]
    if MSN != settings.VIPPS_MERCHANT_SERIAL_NUMBER:
        return HttpResponse(status=400)

    transaction_info = data["transactionInfo"]
    if transaction_info:
        new_status = transaction_info["status"]
        order.status = new_status
        order.save()

    return HttpResponse(status=200)
    # access_token = get_new_access_token()[1]
    # url = f"{settings.VIPPS_ORDER_URL}{order_id}/details"
    # headers = {
    #     "Content-Type": "application/json",
    #     "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
    #     "Authorization": "Bearer " + access_token,
    #     "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
    # }
    # res = requests.get(url, headers=headers)
    # json = res.json()
    # status = json["transactionLogHistory"][0]["operation"]
    # order = Order.objects.get(order_id=order_id)
    # order.status = status
    # order.save()
    # return order


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
