from django.conf import settings

import pytest

from app.payment.enums import OrderStatus
from app.payment.factories import OrderFactory


def get_callback_data(order_id, status):
    return {
        "merchantSerialNumber": settings.VIPPS_MERCHANT_SERIAL_NUMBER,
        "orderId": order_id,
        "transactionInfo": {
            "amount": 20000,
            "status": status,
            "timeStamp": "2018-12-12T11:18:38.246Z",
            "transactionId": "5001420062",
        },
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [
        OrderStatus.RESERVED,
        OrderStatus.CAPTURE,
        OrderStatus.REFUND,
        OrderStatus.CANCEL,
        OrderStatus.SALE,
        OrderStatus.VOID,
    ],
)
def test_update_order_status_by_vipps_callback(default_client, status):
    """Should update order status."""

    order = OrderFactory(status=OrderStatus.INITIATE)
    order_id = order.order_id

    data = get_callback_data(order_id, status)
    response = default_client.post(f"/v2/payments/{order_id}/", data=data)
    order.refresh_from_db()

    assert response.status_code == 200
    assert order.status == status
