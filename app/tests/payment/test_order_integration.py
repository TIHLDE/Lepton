import pytest

from app.content.models.registration import Registration
from rest_framework import status
from app.payment.models.order import Order
from app.payment.factories.paid_event_factory import PaidEventFactory
from datetime import time
from time import sleep
from app.util.test_utils import get_api_client

API_EVENT_BASE_URL = "/events/"
API_PAYMENT_BASE_URL = "/payment/"


def _get_registration_url(event):
    return f"{API_EVENT_BASE_URL}{event.pk}/registrations/"

def _get_order_url():
    return f"{API_PAYMENT_BASE_URL}order/"

def _get_registration_post_data(user, event):
    return {
        "user_id": user.user_id,
        "event": event.pk,
    }

def _get_order_data(user, event):
    return {
        "user_id": user.user_id,
        "event": event.pk
    }

@pytest.mark.django_db
def test_retrieve_own_order_as_member_at_paid_event(member, paid_event):
    data = _get_registration_post_data(member, paid_event)
    client = get_api_client(user=member)
    url = _get_registration_url(event=paid_event.event)
    response = client.post(url, data=data)

    assert response.status_code == 201

    orders = Order.objects.filter(event=paid_event.event, user=member)

    assert len(orders)

    data = _get_order_data(user=member, event=paid_event.event)
    url = _get_order_url()
    response = client.get(url, data=data)

    order = response.data

    assert response.status_code == 200
    assert order is not None

@pytest.mark.django_db
def test_create_as_member_registers_themselves_at_paid_event(member, paid_event):
    """A member should be able to create a registration for themselves."""
    data = _get_registration_post_data(member, paid_event)
    client = get_api_client(user=member)

    url = _get_registration_url(event=paid_event.event)
    response = client.post(url, data=data)
    payment_link = response.data.get("order").get("payment_link")
    
    assert response.status_code == status.HTTP_201_CREATED
    assert payment_link is not None

@pytest.mark.django_db
def test_not_paid_order_is_kicked_of_event_after_timeout(member):
    paid_event = PaidEventFactory(paytime=time(second=3))
    # order = OrderFactory()
    data = _get_registration_post_data(member, paid_event)
    client = get_api_client(user=member)
    url = _get_registration_url(event=paid_event.event)
    response = client.post(url, data=data)

    assert response.status_code == 201
    assert len(Order.objects.all())
    assert len(Registration.objects.all()) == 0