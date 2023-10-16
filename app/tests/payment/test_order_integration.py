import pytest

from app.payment.enums import OrderStatus
from app.util.test_utils import get_api_client

API_PAYMENT_BASE_URL = "/payments/"


def get_order_data(event):
    return {"event": event.id}


@pytest.mark.django_db
def test_create_paid_event_order(user, paid_event):

    client = get_api_client(user=user)
    data = get_order_data(paid_event.event)
    response = client.post(f"{API_PAYMENT_BASE_URL}", data=data)

    order = response.data

    assert response.status_code == 201
    assert order["status"] == OrderStatus.INITIATE
