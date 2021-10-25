from datetime import timedelta

from django.db.models import signals
from django.utils import timezone

import factory
import pytest

from app.common.enums import AdminGroup, GroupType, MembershipType
from app.content.factories import EventFactory
from app.forms.enums import EventFormType
from app.forms.tests.form_factories import EventFormFactory
from app.group.models import Group
from app.util.test_utils import (
    add_user_to_group_with_name,
    get_api_client,
    get_group_type_from_group_name,
)

API_EVENTS_BASE_URL = "/api/v1/events/"


def get_events_url_detail(event=None):
    return f"{API_EVENTS_BASE_URL}{event.pk}/"


def get_event_data(title="New Title", location="New Location", group=None):
    start_date = timezone.now() + timedelta(days=10)
    end_date = timezone.now() + timedelta(days=11)
    data = {
        "title": title,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
    }
    if group:
        data["group"] = group
    return data


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
        "user_member_of_group",
        "event_current_group",
        "event_new_group",
        "expected_status_code",
        "new_title",
    ),
    [
        # Members of admin-groups can edit events if event.group is None
        (AdminGroup.HS, None, None, 200, "Title"),
        (AdminGroup.INDEX, None, None, 200, "Title"),
        (AdminGroup.NOK, None, None, 200, "Title"),
        (AdminGroup.PROMO, None, None, 200, "Title"),
        (AdminGroup.SOSIALEN, None, None, 200, "Title"),
        # Members of admin-groups can edit events if member of the event.group
        (AdminGroup.HS, AdminGroup.HS, None, 200, "Title"),
        (AdminGroup.INDEX, AdminGroup.INDEX, None, 200, "Title"),
        (AdminGroup.NOK, AdminGroup.NOK, None, 200, "Title"),
        (AdminGroup.PROMO, AdminGroup.PROMO, None, 200, "Title"),
        (AdminGroup.SOSIALEN, AdminGroup.SOSIALEN, None, 200, "Title"),
        # HS and Index can edit event if not member of the event.group
        (AdminGroup.HS, AdminGroup.NOK, None, 200, "Title"),
        (AdminGroup.INDEX, AdminGroup.SOSIALEN, None, 200, "Title"),
        # HS and Index can change event.group even if not member of new group
        (AdminGroup.HS, AdminGroup.NOK, AdminGroup.SOSIALEN, 200, "Title"),
        (AdminGroup.INDEX, AdminGroup.SOSIALEN, AdminGroup.PROMO, 200, "Title"),
        # Members of admin-groups can't edit if not member of the event.group
        (AdminGroup.NOK, AdminGroup.PROMO, None, 403, None),
        (AdminGroup.PROMO, AdminGroup.SOSIALEN, None, 403, None),
        (AdminGroup.SOSIALEN, AdminGroup.NOK, None, 403, None),
        # Members of admin-groups can't change event.group if not member of new group
        (AdminGroup.NOK, AdminGroup.NOK, AdminGroup.PROMO, 403, None),
        (AdminGroup.PROMO, AdminGroup.PROMO, AdminGroup.NOK, 403, None,),
        (AdminGroup.SOSIALEN, AdminGroup.SOSIALEN, AdminGroup.NOK, 403, None),
        # Not member of admin group can't update event
        ("Non_admin_group", AdminGroup.NOK, None, 403, None),
        ("Non_admin_group", None, None, 403, None),
    ],
)
@factory.django.mute_signals(signals.post_save)
def test_update_as_board_or_subgroup_group_member(
    user,
    user_member_of_group,
    event_current_group,
    event_new_group,
    expected_status_code,
    new_title,
):
    """
    HS and Index members should be able to update all events.
    Other subgroup members can update events where event.group is their group or None.
    """

    group = (
        Group.objects.get_or_create(
            type=get_group_type_from_group_name(event_current_group),
            name=event_current_group,
        )[0]
        if event_current_group
        else None
    )
    event = EventFactory(group=group)
    expected_title = new_title if new_title else event.title
    new_group = None
    if event_new_group:
        new_group = str(event_new_group)
        print(new_group)
        g = Group.objects.get_or_create(
            type=get_group_type_from_group_name(event_new_group), name=new_group,
        )[0]
        print(g)

    client = get_api_client(user=user, group_name=user_member_of_group)
    url = get_events_url_detail(event)
    data = get_event_data(title=expected_title, group=new_group)

    response = client.put(url, data)
    event.refresh_from_db()

    assert response.status_code == expected_status_code
    assert event.title == expected_title


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "user_member_of_group",
        "membership_type",
        "group_type",
        "event_current_group",
        "event_new_group",
        "expected_status_code",
    ),
    [
        # Leaders of committees and interest-groups can edit events if event.group is None
        ("Kont", MembershipType.LEADER, GroupType.COMMITTEE, None, None, 200),
        ("Py", MembershipType.LEADER, GroupType.INTERESTGROUP, None, None, 200),
        # Leaders of committees and interest-groups can edit events if has access of the event.group
        ("Kont", MembershipType.LEADER, GroupType.COMMITTEE, "Kont", None, 200),
        ("Py", MembershipType.LEADER, GroupType.INTERESTGROUP, "Py", None, 200),
        # Leaders of committees and interest-groups can't edit event if not has access of the event.group
        ("Kont", MembershipType.LEADER, GroupType.COMMITTEE, "Py", None, 403),
        ("Py", MembershipType.LEADER, GroupType.INTERESTGROUP, "Kont", None, 403),
        # Leaders of committees and interest-groups can't change event.group if not has access of new group
        ("Kont", MembershipType.LEADER, GroupType.COMMITTEE, "Kont", "Py", 403),
        ("Py", MembershipType.LEADER, GroupType.INTERESTGROUP, "Py", "Kont", 403),
        # Members of committees and interest-groups can't edit even if member of event.group
        ("Kont", MembershipType.MEMBER, GroupType.COMMITTEE, None, None, 403),
        ("Py", MembershipType.MEMBER, GroupType.INTERESTGROUP, None, None, 403,),
    ],
)
@factory.django.mute_signals(signals.post_save)
def test_update_as_committee_or_interest_group_member(
    user,
    user_member_of_group,
    membership_type,
    group_type,
    event_current_group,
    event_new_group,
    expected_status_code,
):
    """
    Leaders of committees and interest groups should be able to
    update events where event.group is their group or None.
    """

    group = (
        Group.objects.get_or_create(type=group_type, name=event_current_group,)[0]
        if event_current_group
        else None
    )
    event = EventFactory(group=group)
    new_group = None
    if event_new_group:
        new_group = str(event_new_group)
        Group.objects.get_or_create(type=group_type, name=new_group,)[0]

    client = get_api_client(user=user)
    add_user_to_group_with_name(
        user=user,
        group_name=user_member_of_group,
        group_type=group_type,
        membership_type=membership_type,
    )
    url = get_events_url_detail(event)
    data = get_event_data(group=new_group)

    response = client.put(url, data)
    event.refresh_from_db()

    assert response.status_code == expected_status_code


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
    ("user_member_of_group", "event_group", "expected_status_code"),
    [
        # Members of admin-groups can create events with no event.group
        (AdminGroup.HS, None, 201),
        (AdminGroup.INDEX, None, 201),
        (AdminGroup.NOK, None, 201),
        (AdminGroup.PROMO, None, 201),
        (AdminGroup.SOSIALEN, None, 201),
        # Members of admin-groups can create events when member of the event.group
        (AdminGroup.HS, AdminGroup.HS, 201),
        (AdminGroup.INDEX, AdminGroup.INDEX, 201),
        (AdminGroup.NOK, AdminGroup.NOK, 201),
        (AdminGroup.PROMO, AdminGroup.PROMO, 201),
        (AdminGroup.SOSIALEN, AdminGroup.SOSIALEN, 201),
        # HS and Index can create event also when not member of the event.group
        (AdminGroup.HS, AdminGroup.NOK, 201),
        (AdminGroup.INDEX, AdminGroup.NOK, 201),
        # Members of admin-groups can't create event if not member of the event.group
        (AdminGroup.NOK, AdminGroup.PROMO, 403),
        (AdminGroup.PROMO, AdminGroup.SOSIALEN, 403),
        (AdminGroup.SOSIALEN, AdminGroup.NOK, 403),
        # Not member of admin group can't create event
        ("Non_admin_group", None, 403),
        ("Non_admin_group", None, 403),
    ],
)
@factory.django.mute_signals(signals.post_save)
def test_create_as_board_or_subgroup_group_member(
    user, user_member_of_group, event_group, expected_status_code,
):
    """
    HS and Index members should be able to create events no matter which group is selected.
    Other subgroup members can create events where event.group is their group or None.
    """

    new_group = None
    if event_group:
        new_group = str(event_group)
        Group.objects.get_or_create(
            type=get_group_type_from_group_name(event_group), name=new_group,
        )[0]

    client = get_api_client(user=user, group_name=user_member_of_group)
    data = get_event_data(group=new_group)

    response = client.post(API_EVENTS_BASE_URL, data)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "user_member_of_group",
        "membership_type",
        "group_type",
        "event_group",
        "expected_status_code",
    ),
    [
        # Leaders of committees and interest-groups can create events with no event.group
        ("Kont", MembershipType.LEADER, GroupType.COMMITTEE, None, 201),
        ("Py", MembershipType.LEADER, GroupType.INTERESTGROUP, None, 201),
        # Leaders of committees and interest-groups can create events when leader of the event.group
        ("Kont", MembershipType.LEADER, GroupType.COMMITTEE, "Kont", 201),
        ("Py", MembershipType.LEADER, GroupType.INTERESTGROUP, "Py", 201),
        # Leaders of committees and interest-groups can't create event if not has access to the event.group
        ("Kont", MembershipType.LEADER, GroupType.COMMITTEE, "Py", 403),
        ("Py", MembershipType.LEADER, GroupType.INTERESTGROUP, "Kont", 403),
        # Members of committees and interest-groups can't create event even if member of event.group
        ("Kont", MembershipType.MEMBER, GroupType.COMMITTEE, "Kont", 403),
        ("Py", MembershipType.MEMBER, GroupType.INTERESTGROUP, None, 403,),
    ],
)
@factory.django.mute_signals(signals.post_save)
def test_create_as_committee_or_interest_group_leader(
    user,
    user_member_of_group,
    membership_type,
    group_type,
    event_group,
    expected_status_code,
):
    """
    Leaders of committees and interest groups should be able to
    update events where event.group is their group or None.
    """

    new_group = None
    if event_group:
        new_group = str(event_group)
        Group.objects.get_or_create(type=group_type, name=new_group,)[0]

    client = get_api_client(user=user)
    add_user_to_group_with_name(
        user=user,
        group_name=user_member_of_group,
        group_type=group_type,
        membership_type=membership_type,
    )
    data = get_event_data(group=new_group)

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
