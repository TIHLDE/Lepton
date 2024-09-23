from datetime import timedelta

from django.utils import timezone

import pytest

from app.common.enums import NativeGroupType as GroupType
from app.content.models.event import Event
from app.group.models.group import Group
from app.payment.factories.paid_event_factory import PaidEventFactory
from app.payment.models.paid_event import PaidEvent
from app.util.test_utils import get_api_client

API_EVENTS_BASE_URL = "/events/"


def _get_registration_url(event):
    return f"{API_EVENTS_BASE_URL}{event.pk}/registrations/"


def get_events_url_detail(event=None):
    return f"{API_EVENTS_BASE_URL}{event.pk}/"


def get_paid_event_data(
    title="New Title",
    location="New Location",
    organizer=None,
    price=100.00,
    paytime="01:00:00",
    is_paid_event=True,
):
    start_date = timezone.now() + timedelta(days=10)
    end_date = timezone.now() + timedelta(days=11)
    data = {
        "title": title,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "is_paid_event": is_paid_event,
        "paid_information": {"price": price, "paytime": paytime},
    }
    if organizer:
        data["organizer"] = organizer
    return data


def _get_registration_post_data(user, event):
    return {
        "user_id": user.user_id,
        "event": event.pk,
    }


def get_paid_event_without_price_data(
    title="New Title", location="New Location", organizer=None, is_paid_event=True
):
    start_date = timezone.now() + timedelta(days=10)
    end_date = timezone.now() + timedelta(days=11)
    data = {
        "title": title,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "is_paid_event": is_paid_event,
    }
    if organizer:
        data["organizer"] = organizer
    return data


@pytest.mark.django_db
def test_create_paid_event_as_admin(admin_user):
    """
    HS and Index members should be able to create paid events.
    """

    organizer = Group.objects.get_or_create(name="HS", type=GroupType.BOARD)[0]
    client = get_api_client(user=admin_user)
    data = get_paid_event_data(organizer=organizer.slug)

    response = client.post(API_EVENTS_BASE_URL, data)
    created_event = Event.objects.get(title=data["title"])
    paid_event_information = PaidEvent.objects.get(event=created_event)

    assert response.status_code == 201
    assert created_event.is_paid_event
    assert paid_event_information.price == data["paid_information"]["price"]
    assert (
        float(response.data["paid_information"]["price"])
        == data["paid_information"]["price"]
    )


@pytest.mark.django_db
def test_create_paid_event_without_price_as_admin(admin_user):
    """
    HS and Index members should not be able to create a paid event wihtout a price and paytime.
    Then there should be created a normal event.
    """

    organizer = Group.objects.get_or_create(name="HS", type=GroupType.BOARD)[0]
    client = get_api_client(user=admin_user)
    data = get_paid_event_without_price_data(organizer=organizer.slug)

    response = client.post(API_EVENTS_BASE_URL, data)
    created_event = Event.objects.get(title=data["title"])

    assert response.status_code == 201
    assert not created_event.is_paid_event


@pytest.mark.django_db
def test_update_paid_event_as_admin(admin_user):
    """
    HS and Index members should be able to update all paid events.
    Other subgroup members can update paid events where event.organizer is their group or None.
    Leaders of committees and interest groups should be able to
    update events where event.organizer is their group or None.
    """

    new_event_price = 100.00
    paid_event = PaidEventFactory(price=0.00)
    event = paid_event.event
    organizer = Group.objects.get_or_create(name="HS", type=GroupType.BOARD)[0]
    client = get_api_client(user=admin_user)
    url = get_events_url_detail(event)
    data = get_paid_event_data(organizer=organizer.slug)

    response = client.put(url, data)
    event.refresh_from_db()

    assert response.status_code == 200
    assert event.paid_information.price == new_event_price
    assert float(response.data["paid_information"]["price"]) == new_event_price


@pytest.mark.django_db
@pytest.mark.skip(
    reason="This is handled in the frontend. Should be refactored in backend."
)
def test_update_paid_event_to_free_event_with_registrations_as_admin(
    admin_user, registration
):
    """
    HS and Index members should not be able to update a paid event with registrations to a free event.
    Other subgroup members can update paid events where event.organizer is their group or None.
    Leaders of committees and interest groups should be able to
    update events where event.organizer is their group or None.
    """

    paid_event = PaidEventFactory(price=100.00)
    event = paid_event.event

    registration.event = event
    registration.save()

    organizer = Group.objects.get_or_create(name="HS", type=GroupType.BOARD)[0]
    client = get_api_client(user=admin_user)
    url = get_events_url_detail(event)
    data = get_paid_event_data(organizer=organizer.slug, is_paid_event=False)

    response = client.put(url, data)
    event.refresh_from_db()

    assert response.status_code == 400
    assert event.is_paid_event


@pytest.mark.django_db
def test_update_paid_event_to_free_event_without_registrations_as_admin(admin_user):
    """
    HS and Index members should be able to update a paid event without registrations to a free event.
    Other subgroup members can update paid events where event.organizer is their group or None.
    Leaders of committees and interest groups should be able to
    update events where event.organizer is their group or None.
    """

    paid_event = PaidEventFactory(price=100.00)
    event = paid_event.event

    organizer = Group.objects.get_or_create(name="HS", type=GroupType.BOARD)[0]
    client = get_api_client(user=admin_user)
    url = get_events_url_detail(event)
    data = get_paid_event_data(organizer=organizer.slug, is_paid_event=False)

    response = client.put(url, data)
    event.refresh_from_db()

    assert response.status_code == 200
    assert not event.is_paid_event
