from datetime import timedelta

from django.db.models import signals
from django.utils import timezone

import factory
import pytest

from app.common.enums import AdminGroup, GroupType, MembershipType
from app.content.factories import EventFactory
from app.forms.enums import EventFormType
from app.forms.tests.form_factories import EventFormFactory
from app.group.models import Group, Membership
from app.util.test_utils import get_api_client

API_EVENTS_BASE_URL = "/api/v1/events/"


def get_events_url_detail(event=None):
    return f"{API_EVENTS_BASE_URL}{event.pk}/"


def get_event_data():
    start_date = timezone.now() + timedelta(days=10)
    end_date = timezone.now() + timedelta(days=11)
    return {
        "title": "New Title",
        "location": "New Location",
        "start_date": start_date,
        "end_date": end_date,
    }


@pytest.mark.django_db
def test_list_as_anonymous_user(default_client):
    """An anonymous user should be able to list all events."""
    response = default_client.get(API_EVENTS_BASE_URL)
    assert response.status_code == 200


@pytest.mark.django_db
def test_retrieve_as_anonymous_user(default_client, event):
    """An anonymous user should be able to retrieve an event."""
    url = get_events_url_detail(event)
    response = default_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_as_anonymous_user(default_client, event):
    """An anonymous user should not be able to update an event entity."""

    data = get_event_data()
    url = get_events_url_detail(event)
    response = default_client.put(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_update_as_user(event, user):
    """A user should not be able to update an event entity."""

    data = get_event_data()
    url = get_events_url_detail(event)
    client = get_api_client(user=user)
    response = client.put(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "membership_group_name",
        "group_type",
        "event_group_name",
        "membership_type",
        "expected_status_code",
        "new_title",
    ),
    [
        # Members of admin-groups can edit events if event.group is None
        (AdminGroup.HS, None, None, None, 200, "New Title"),
        (AdminGroup.INDEX, None, None, None, 200, "New Title"),
        (AdminGroup.NOK, None, None, None, 200, "New Title"),
        (AdminGroup.PROMO, None, None, None, 200, "New Title"),
        (AdminGroup.SOSIALEN, None, None, None, 200, "New Title"),
        # Members of admin-groups can edit events if member of the event.group
        (AdminGroup.HS, None, AdminGroup.HS, None, 200, "New Title"),
        (AdminGroup.INDEX, None, AdminGroup.INDEX, None, 200, "New Title"),
        (AdminGroup.NOK, None, AdminGroup.NOK, None, 200, "New Title"),
        (AdminGroup.PROMO, None, AdminGroup.PROMO, None, 200, "New Title"),
        (AdminGroup.SOSIALEN, None, AdminGroup.SOSIALEN, None, 200, "New Title"),
        # HS and Index can edit even if not member of the event.group
        (AdminGroup.HS, None, AdminGroup.NOK, None, 200, "New Title"),
        (AdminGroup.INDEX, None, AdminGroup.SOSIALEN, None, 200, "New Title"),
        # Members of admin-groups can't edit if not member of the event.group
        (AdminGroup.NOK, None, AdminGroup.PROMO, None, 403, None),
        (AdminGroup.PROMO, None, AdminGroup.SOSIALEN, None, 403, None),
        (AdminGroup.SOSIALEN, None, AdminGroup.NOK, None, 403, None),
        # Committees and interest-group leaders can edit events if leader of the event.group
        (
            "Kontkom",
            GroupType.COMMITTEE,
            "Kontkom",
            MembershipType.LEADER,
            200,
            "New Title",
        ),
        (
            "Pythons",
            GroupType.INTERESTGROUP,
            "Pythons",
            MembershipType.LEADER,
            200,
            "New Title",
        ),
        # Committees and interest-group members can't edit events if member of the event.group
        ("Kontkom", GroupType.COMMITTEE, "Kontkom", None, 403, None),
        ("Pythons", GroupType.INTERESTGROUP, "Pythons", None, 403, None),
        # Not member of admin, committee or interest group
        ("Non_admin_group", None, AdminGroup.NOK, None, 403, None),
        ("Non_admin_group", None, None, None, 403, None),
    ],
)
@factory.django.mute_signals(signals.post_save)
def test_update_as_admin_user(
    user,
    membership_group_name,
    group_type,
    event_group_name,
    membership_type,
    expected_status_code,
    new_title,
):
    """
    HS and Index members should be able to update all events.
    Other subgroup members and leaders of committees and interest groups should be able to
    update events where event.group is their group or None.
    """

    group = (
        None
        if event_group_name is None
        else Group.objects.get_or_create(
            type=group_type if group_type is not None else GroupType.SUBGROUP,
            name=event_group_name,
        )[0]
    )
    event = EventFactory(group=group)
    expected_title = new_title if new_title else event.title
    data = get_event_data()
    url = get_events_url_detail(event)
    client = get_api_client(user=user)
    membership_group = Group.objects.get_or_create(
        type=group_type if group_type is not None else GroupType.SUBGROUP,
        name=membership_group_name,
    )[0]
    Membership.objects.create(
        group=membership_group,
        user=user,
        membership_type=membership_type
        if membership_type is not None
        else MembershipType.MEMBER,
    )

    response = client.put(url, data)
    event.refresh_from_db()

    assert response.status_code == expected_status_code
    assert event.title == expected_title


@pytest.mark.django_db
def test_create_as_anonymous_user(default_client):
    """An anonymous user should not be able to create an event entity."""

    data = get_event_data()
    response = default_client.post(API_EVENTS_BASE_URL, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_as_user(user):
    """A user should not be able to create an event entity."""

    data = get_event_data()
    client = get_api_client(user=user)
    response = client.post(API_EVENTS_BASE_URL, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, 201),
        (AdminGroup.INDEX, 201),
        (AdminGroup.NOK, 201),
        (AdminGroup.PROMO, 201),
        (AdminGroup.SOSIALEN, 201),
        ("Non_admin_group", 403),
    ],
)
def test_create_as_admin_user(user, group_name, expected_status_code):
    """Only users in an admin group should be able to create an event entity."""

    data = get_event_data()
    client = get_api_client(user=user, group_name=group_name)
    response = client.post(API_EVENTS_BASE_URL, data)
    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_delete_as_anonymous_user(default_client, event):
    """An anonymous user should not be able to delete an event entity."""
    url = get_events_url_detail(event)
    response = default_client.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_as_user(user, event):
    """A user should not be able to to delete an event entity."""
    client = get_api_client(user=user)
    url = get_events_url_detail(event)
    response = client.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, 200),
        (AdminGroup.INDEX, 200),
        (AdminGroup.NOK, 200),
        (AdminGroup.PROMO, 200),
        (AdminGroup.SOSIALEN, 200),
        ("Non_admin_group", 403),
    ],
)
def test_delete_as_group_members(event, user, group_name, expected_status_code):
    """Only users in an admin group should be able to delete an event entity."""
    client = get_api_client(user=user, group_name=group_name)
    url = get_events_url_detail(event)
    response = client.delete(url)
    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_retrieve_event_includes_form_evaluation(default_client, event):
    """Should include the id of the related form evaluation in the response."""
    evaluation = EventFormFactory(type=EventFormType.EVALUATION)
    event.forms.add(evaluation)
    event.save()
    url = get_events_url_detail(event)
    response = default_client.get(url)

    assert response.json().get("evaluation") == str(evaluation.id)


@pytest.mark.django_db
def test_retrieve_event_includes_form_survey(default_client, event):
    """Should include the id of the related form survey in the response."""
    survey = EventFormFactory(type=EventFormType.SURVEY)
    event.forms.add(survey)
    event.save()
    url = get_events_url_detail(event)
    response = default_client.get(url)

    assert response.json().get("survey") == str(survey.id)
