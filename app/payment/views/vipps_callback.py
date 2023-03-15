from app.payment.models.order import Order
from app.payment.enums import OrderStatus
from django.conf import settings
from app.payment.util.payment_utils import get_new_access_token
import requests

def vipps_callback(request):
    try:
        order_id = request["orderId"]
        access_token = get_new_access_token()[1]
        url = f"https://apitest.vipps.no/ecomm/v2/payments/{order_id}/details"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
            "Authorization": "Bearer " + access_token,
            "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
            "Cookie": "fpc=AqiUsXVZL3NFr4JO1-F_-NRQ2zIJAQAAAGhUfNsOAAAA; stsservicecookie=estsfd; x-ms-gateway-slice=estsfd",
        }
        res = requests.get(url, headers=headers)
        json = res.json()
        status = json["transactionLogHistory"][0]["operation"]
        order = Order.objects.get(order_id=order_id)
        order.status = status
        order.save()
        return status
    except Exception as e:
        print(e)

def force_payment(order_id):
    try:
        access_token = get_new_access_token()[1]
        url = f"https://apitest.vipps.no/ecomm/v2/integration-test/payments/{order_id}/approve"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": settings.VIPPS_SUBSCRIPTION_KEY,
            "Authorization": "Bearer " + access_token,
            "Merchant-Serial-Number": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
            "Cookie": "fpc=AqiUsXVZL3NFr4JO1-F_-NRQ2zIJAQAAAGhUfNsOAAAA; stsservicecookie=estsfd; x-ms-gateway-slice=estsfd",
        }

        res = requests.post(url, headers=headers)
        status_code = res.status_code
        json = res.json()
        return (json, status_code)
    except Exception as e:
        print(e)