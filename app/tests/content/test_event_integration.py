from datetime import timedelta

from django.db.models import signals
from django.utils import timezone

import factory
import pytest

from app.common.enums import AdminGroup, GroupType, MembershipType
from app.content.factories import EventFactory
from app.forms.enums import EventFormType
from app.forms.tests.form_factories import EventFormFactory
from app.group.factories import GroupFactory
from app.group.models import Group
from app.util.test_utils import (
    add_user_to_group_with_name,
    get_api_client,
    get_group_type_from_group_name,
)

API_EVENTS_BASE_URL = "/api/v1/events/"


def get_events_url_detail(event=None):
    return f"{API_EVENTS_BASE_URL}{event.pk}/"


def get_event_data(title="New Title", location="New Location", organizer=None):
    start_date = timezone.now() + timedelta(days=10)
    end_date = timezone.now() + timedelta(days=11)
    data = {
        "title": title,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
    }
    if organizer:
        data["organizer"] = organizer
    return data


# "event_current_organizer"/"event_new_organizer" should have one of 3 different values:
# - None -> The event has no connected organizer/should remove connection to organizer
# - "same" -> The event is connected to/should be connected to same organizer as user is member of
# - "other" -> The event is connected to/should be connected to another organizer as user i member of
permission_params = pytest.mark.parametrize(
    (
        "user_member_of_organizer",
        "membership_type",
        "organizer_type",
        "event_current_organizer",
        "event_new_organizer",
        "expected_status_code",
    ),
    (
        # Members of admin-organizers have access if event.organizer is None
        (AdminGroup.HS, None, None, None, None, 200),
        (AdminGroup.INDEX, None, None, None, None, 200),
        (AdminGroup.NOK, None, None, None, None, 200),
        (AdminGroup.PROMO, None, None, None, None, 200),
        (AdminGroup.SOSIALEN, None, None, None, None, 200),
        # Members of admin-organizers have access if member of the event.organizer
        (AdminGroup.HS, None, None, "same", None, 200),
        (AdminGroup.INDEX, None, None, "same", None, 200),
        (AdminGroup.NOK, None, None, "same", None, 200),
        (AdminGroup.PROMO, None, None, "same", None, 200),
        (AdminGroup.SOSIALEN, None, None, "same", None, 200),
        # HS and Index have access if not member of the event.organizer
        (AdminGroup.HS, None, None, "other", None, 200),
        (AdminGroup.INDEX, None, None, "other", None, 200),
        # HS and Index have access even if not member of new organizer
        (AdminGroup.HS, None, None, "other", "other", 200),
        (AdminGroup.INDEX, None, None, "other", "other", 200),
        # Members of admin-organizers don't have access if not member of the event.organizer
        (AdminGroup.NOK, None, None, "other", None, 403),
        (AdminGroup.PROMO, None, None, "other", None, 403),
        (AdminGroup.SOSIALEN, None, None, "other", None, 403),
        # Members of admin-organizers don't have access if not member of new organizer
        (AdminGroup.NOK, None, None, "same", "other", 403),
        (AdminGroup.PROMO, None, None, "same", "other", 403),
        (AdminGroup.SOSIALEN, None, None, "same", "other", 403),
        # Not member of admin organizer don't have access
        ("Non_admin_group", None, None, "other", None, 403),
        ("Non_admin_group", None, None, None, None, 403),
        # Leaders of committees and interest-organizers have access if event.organizer is None
        ("Kont", MembershipType.LEADER, GroupType.COMMITTEE, None, None, 200),
        ("Py", MembershipType.LEADER, GroupType.INTERESTGROUP, None, None, 200),
        # Leaders of committees and interest-organizers have access if has access of the event.organizer
        ("Kont", MembershipType.LEADER, GroupType.COMMITTEE, "same", None, 200),
        ("Py", MembershipType.LEADER, GroupType.INTERESTGROUP, "same", None, 200),
        # Leaders of committees and interest-organizers don't have access if not has access of the event.organizer
        ("Kont", MembershipType.LEADER, GroupType.COMMITTEE, "other", None, 403),
        ("Py", MembershipType.LEADER, GroupType.INTERESTGROUP, "other", None, 403),
        # Leaders of committees and interest-organizers don't have access if not has access of new organizer
        ("Kont", MembershipType.LEADER, GroupType.COMMITTEE, "same", "other", 403),
        ("Py", MembershipType.LEADER, GroupType.INTERESTGROUP, "same", "other", 403),
        # Members of committees and interest-organizers don't have access even if member of event.organizer
        ("Kont", MembershipType.MEMBER, GroupType.COMMITTEE, None, None, 403),
        ("Py", MembershipType.MEMBER, GroupType.INTERESTGROUP, None, None, 403),
    ),
)


@pytest.fixture
@permission_params
def permission_test_util(
    user,
    user_member_of_organizer,
    membership_type,
    organizer_type,
    event_current_organizer,
    event_new_organizer,
    expected_status_code,
):
    user_organizer_type = (
        organizer_type
        if organizer_type
        else get_group_type_from_group_name(user_member_of_organizer)
    )

    organizer = None
    if event_current_organizer == "same":
        organizer = Group.objects.get_or_create(
            type=user_organizer_type, name=user_member_of_organizer,
        )[0]
    elif event_current_organizer == "other":
        organizer = GroupFactory()

    event = EventFactory(organizer=organizer)
    expected_title = "Title" if expected_status_code == 200 else event.title
    new_organizer = None
    if event_new_organizer == "same":
        new_organizer = Group.objects.get_or_create(
            type=user_organizer_type, name=user_member_of_organizer,
        )[0]
        new_organizer = new_organizer.slug
    elif event_new_organizer == "other":
        new_organizer = GroupFactory()
        new_organizer = new_organizer.slug

    add_user_to_group_with_name(
        user=user,
        group_name=user_member_of_organizer,
        group_type=user_organizer_type,
        membership_type=membership_type if membership_type else MembershipType.MEMBER,
    )

    return (
        user,
        event,
        new_organizer,
        expected_title,
        expected_status_code,
        event_current_organizer,
        event_new_organizer,
    )


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
@permission_params
@factory.django.mute_signals(signals.post_save)
def test_update_event_as_admin(permission_test_util):
    """
    HS and Index members should be able to update all events.
    Other subgroup members can update events where event.organizer is their group or None.
    Leaders of committees and interest groups should be able to
    update events where event.organizer is their group or None.
    """

    (
        user,
        event,
        new_organizer,
        expected_title,
        expected_status_code,
        _,
        _,
    ) = permission_test_util

    client = get_api_client(user=user)
    url = get_events_url_detail(event)
    data = get_event_data(title=expected_title, organizer=new_organizer)

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
@permission_params
@factory.django.mute_signals(signals.post_save)
def test_create_event_as_admin(permission_test_util):
    """
    HS and Index members should be able to create events no matter which organizer is selected.
    Other subgroup members can create events where event.organizer is their group or None.
    Leaders of committees and interest groups should be able to
    update events where event.organizer is their group or None.
    """

    (user, _, new_organizer, _, expected_status_code, _, _,) = permission_test_util

    client = get_api_client(user=user)
    data = get_event_data(organizer=new_organizer)

    response = client.post(API_EVENTS_BASE_URL, data)

    assert (
        response.status_code == 201
        if expected_status_code == 200
        else expected_status_code
    )


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
@permission_params
@factory.django.mute_signals(signals.post_save)
def test_delete_event_as_admin(permission_test_util):
    """
    HS and Index members should be able to delete events no matter which organizer is selected.
    Other subgroup members can delete events where event.organizer is their group or None.
    Leaders of committees and interest groups should be able to
    delete events where event.organizer is their group or None.
    """

    (
        user,
        event,
        _,
        _,
        expected_status_code,
        _,
        event_new_organizer,
    ) = permission_test_util

    # These tests only apply to create and delete to ensure that you can't create an
    # event for another organizer, and therefore expects 403. In delete we don't change organizer
    # and the user should therefore be allowed to delete the event
    if event_new_organizer == "other":
        expected_status_code = 200

    client = get_api_client(user=user)
    url = get_events_url_detail(event)
    response = client.delete(url)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "member_of_organizer",
        "organizer_type",
        "membership_type",
        "expected_events_amount",
    ),
    [
        (AdminGroup.HS, GroupType.BOARD, MembershipType.MEMBER, 9),
        (AdminGroup.INDEX, GroupType.SUBGROUP, MembershipType.MEMBER, 9),
        (AdminGroup.NOK, GroupType.SUBGROUP, MembershipType.MEMBER, 3),
        (AdminGroup.SOSIALEN, GroupType.SUBGROUP, MembershipType.MEMBER, 2),
        (AdminGroup.PROMO, GroupType.SUBGROUP, MembershipType.MEMBER, 2),
        ("Pythons", GroupType.INTERESTGROUP, MembershipType.LEADER, 2),
        ("KontKom", GroupType.COMMITTEE, MembershipType.LEADER, 2),
        ("Pythons", GroupType.INTERESTGROUP, MembershipType.MEMBER, 0),
        ("KontKom", GroupType.COMMITTEE, MembershipType.MEMBER, 0),
        ("Not_admin", GroupType.OTHER, MembershipType.MEMBER, 0),
    ],
)
def test_retrieve_events_where_is_admin_only_includes_events_where_is_admin(
    user, member_of_organizer, organizer_type, membership_type, expected_events_amount
):
    """When retrieving events where is admin, only events where is admin should be returned"""

    hs = GroupFactory(type=GroupType.BOARD, name=AdminGroup.HS, slug=AdminGroup.HS)
    index = GroupFactory(
        type=GroupType.SUBGROUP, name=AdminGroup.INDEX, slug=AdminGroup.INDEX
    )
    nok = GroupFactory(
        type=GroupType.SUBGROUP, name=AdminGroup.NOK, slug=AdminGroup.NOK
    )
    sosialen = GroupFactory(
        type=GroupType.SUBGROUP, name=AdminGroup.SOSIALEN, slug=AdminGroup.SOSIALEN
    )
    promo = GroupFactory(
        type=GroupType.SUBGROUP, name=AdminGroup.PROMO, slug=AdminGroup.PROMO
    )
    kontkom = GroupFactory(type=GroupType.COMMITTEE, name="KontKom", slug="kontkom")
    pythons = GroupFactory(type=GroupType.INTERESTGROUP, name="Pythons", slug="pythons")

    EventFactory(organizer=hs)
    EventFactory(organizer=index)
    EventFactory(organizer=nok)
    EventFactory(organizer=nok)
    EventFactory(organizer=sosialen)
    EventFactory(organizer=promo)
    EventFactory(organizer=kontkom)
    EventFactory(organizer=pythons)
    EventFactory()

    client = get_api_client(user=user)
    add_user_to_group_with_name(
        user=user,
        group_name=member_of_organizer,
        group_type=organizer_type,
        membership_type=membership_type,
    )

    url = f"{API_EVENTS_BASE_URL}/admin/"
    response = client.get(url)

    assert int(response.json().get("count")) == expected_events_amount


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
