from app.content.models.registration import Registration
from rest_framework import status

import pytest
from app.content.factories.registration_factory import RegistrationFactory
from app.payment.models.order import Order
from app.payment.factories.order_factory import OrderFactory
from app.payment.factories.paid_event_factory import PaidEventFactory
from datetime import time
from time import sleep

from app.util.test_utils import get_api_client

API_EVENT_BASE_URL = "/events/"


def _get_registration_url(event):
    return f"{API_EVENT_BASE_URL}{event.pk}/registrations/"


def _get_registration_post_data(user, event):
    return {
        "user_id": user.user_id,
        "event": event.pk,
    }


@pytest.mark.django_db
def test_create_as_member_registers_themselves_at_paid_event(member, paid_event):
    """A member should be able to create a registration for themselves."""
    data = _get_registration_post_data(member, paid_event)
    client = get_api_client(user=member)

    url = _get_registration_url(event=paid_event)
    response = client.post(url, data=data)

    payment_link = response.data.get("order").get("payment_link")
    
    assert response.status_code == status.HTTP_201_CREATED
    assert payment_link is not None

@pytest.mark.django_db
def test_not_paid_order_is_kicked_of_event_after_timeout(member):
    paid_event = PaidEventFactory(paytime=time(second=30))
    order = OrderFactory()
    data = _get_registration_post_data(member, paid_event)
    client = get_api_client(user=member)
    url = _get_registration_url(event=paid_event)
    response = client.post(url, data=data)
    regs = Registration.objects.all()
    print(regs)
    print(len(regs))

    assert response.status_code == 201
    assert len(Order.objects.all())
    assert len(Registration.objects.all())


    sleep(35)

    assert len(Registration.objects.all()) == 0
    
    
    # Lag event med lav tid
    # Lag ordre
    # Skjekk at ordre er inne i systemet
    # Vent noen sekunder
    # Skjekk at ordre er vekke

