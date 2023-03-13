from app.payment.models.order import Order
from app.payment.enums import OrderStatus
import requests

def vipps_callback(request):
    try:
        order_id = request["orderId"]
        res = requests.get("INSERT VIPPS API AND SEND order_id")
        json = res.json()
        status = json["transactionLogHistory"][0]["operation"]
        order = Order.objects.get(order_id=order_id)
        order.update(status=status)
    except Exception as e:
        print(e)