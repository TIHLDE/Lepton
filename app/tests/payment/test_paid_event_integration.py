import pytest
from datetime import timedelta
from django.utils import timezone
from app.common.enums import AdminGroup, GroupType, MembershipType
from app.content.models.event import Event
from app.group.models.group import Group
from app.payment.models.paid_event import PaidEvent
from app.util.test_utils import (
    add_user_to_group_with_name,
    get_api_client,
    get_group_type_from_group_name,
)

API_EVENTS_BASE_URL = "/events/"

def get_paid_event_data(title="New Title", location="New Location", organizer=None):
    start_date = timezone.now() + timedelta(days=10)
    end_date = timezone.now() + timedelta(days=11)
    data = {
        "title": title,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "paid_information": {
            "price": 100.00,
        },
    }
    if organizer:
        data["organizer"] = organizer
    return data


@pytest.mark.django_db
def test_create_paid_event_as_admin(admin_user):
    """
    HS and Index members should be able to create events no matter which organizer is selected.
    Other subgroup members can create events where event.organizer is their group or None.
    Leaders of committees and interest groups should be able to
    update events where event.organizer is their group or None.
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
    assert float(response.data["paid_information"]["price"]) == data["paid_information"]["price"]
