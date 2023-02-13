from rest_framework import status

import pytest

from app.common.enums import AdminGroup, GroupType, MembershipType
from app.content.factories import EventFactory, RegistrationFactory, UserFactory
from app.content.factories.priority_pool_factory import PriorityPoolFactory
from app.forms.enums import EventFormType
from app.forms.tests.form_factories import EventFormFactory, SubmissionFactory
from app.group.factories import GroupFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client
from app.util.utils import now

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
    print(response.data)

    payment_link = response.data.get("payment_link")

    assert response.status_code == status.HTTP_201_CREATED
    assert payment_link is not None
