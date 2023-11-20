from datetime import timedelta

from django.utils import timezone
from rest_framework import status

import pytest

from app.common.enums import AdminGroup, Groups, GroupType, MembershipType
from app.content.factories import EventFactory, RegistrationFactory, UserFactory
from app.content.models import Category, Event
from app.forms.enums import EventFormType
from app.forms.tests.form_factories import EventFormFactory
from app.group.factories import GroupFactory
from app.group.models import Group
from app.util import now
from app.util.test_utils import (
    add_user_to_group_with_name,
    get_api_client,
    get_group_type_from_group_name,
)

API_EVENTS_BASE_URL = "/events/"


def get_events_url_detail(event=None):
    return f"{API_EVENTS_BASE_URL}{event.pk}/"


def get_event_data(
    title="New Title",
    location="New Location",
    organizer=None,
    contact_person=None,
    limit=0,
):
    start_date = timezone.now() + timedelta(days=10)
    end_date = timezone.now() + timedelta(days=11)
    data = {
        "title": title,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "is_paid_event": False,
        "limit": limit,
    }
    if organizer:
        data["organizer"] = organizer
    if contact_person:
        data["contact_person"] = contact_person
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
        (AdminGroup.PROMO, None, None, "other", None, 200),
        # HS and Index have access even if not member of new organizer
        (AdminGroup.HS, None, None, "other", "other", 200),
        (AdminGroup.INDEX, None, None, "other", "other", 200),
        (AdminGroup.PROMO, None, None, "other", None, 200),
        # Members of admin-organizers don't have access if not member of the event.organizer
        (AdminGroup.NOK, None, None, "other", None, 403),
        (AdminGroup.SOSIALEN, None, None, "other", None, 403),
        # Members of admin-organizers don't have access if not member of new organizer
        (AdminGroup.NOK, None, None, "same", "other", 403),
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
            type=user_organizer_type,
            name=user_member_of_organizer,
        )[0]
    elif event_current_organizer == "other":
        organizer = GroupFactory()

    event = EventFactory(organizer=organizer)
    expected_title = "Title" if expected_status_code == 200 else event.title
    new_organizer = None
    if event_new_organizer == "same":
        new_organizer = Group.objects.get_or_create(
            type=user_organizer_type,
            name=user_member_of_organizer,
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
def test_list_as_anonymous_user(default_client, event):
    """An anonymous user should be able to list all events that are not activities."""

    category = Category.objects.create(text="Aktivitet")
    activity = EventFactory(category=category)

    activity.category = category
    activity.save()

    event.category = None
    event.save()

    response = default_client.get(API_EVENTS_BASE_URL)
    assert response.status_code == 200
    assert response.json().get("count") == 1


@pytest.mark.django_db
def test_list_activities_as_anonymous_user(default_client, event):
    """An anonymous user should be able to list all activities."""

    category = Category.objects.create(text="Aktivitet")
    activity = EventFactory(category=category)

    activity.category = category
    activity.save()

    event.category = None
    event.save()

    response = default_client.get(f"{API_EVENTS_BASE_URL}?activity=true")

    assert response.status_code == 200
    assert response.json().get("count") == 1


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
    data = get_event_data(
        title=expected_title, organizer=new_organizer, limit=event.limit
    )

    response = client.put(url, data)
    event.refresh_from_db()

    assert response.status_code == expected_status_code
    assert event.title == expected_title


@pytest.mark.django_db
def test_update_event_with_increased_limit(admin_user, event):
    """
    Admins should be able to update the limit of an event.
    Then the first person on the waiting list should be moved to the queue.
    Priorities should be respected.
    """

    event.limit = 1
    event.save()

    registration = RegistrationFactory(event=event)
    waiting_registration = RegistrationFactory(event=event)

    assert not registration.is_on_wait
    assert waiting_registration.is_on_wait
    assert event.waiting_list_count == 1

    client = get_api_client(user=admin_user)
    url = get_events_url_detail(event)
    data = get_event_data(limit=2)

    response = client.put(url, data)
    event.refresh_from_db()
    registration.refresh_from_db()
    waiting_registration.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert event.limit == 2
    assert event.waiting_list_count == 0
    assert not waiting_registration.is_on_wait


@pytest.mark.django_db
def test_update_event_with_decreased_limit(
    admin_user, event_with_priority_pool, user_in_priority_pool
):
    """
    Admins should be able to update the limit of an event.
    Then the first person on the queue should be moved to the waiting list.
    Priorities should be respected.
    """

    event_with_priority_pool.limit = 4
    event_with_priority_pool.save()

    registration = RegistrationFactory(event=event_with_priority_pool)
    first_queue_registration = RegistrationFactory(event=event_with_priority_pool)
    second_queue_registration = RegistrationFactory(event=event_with_priority_pool)
    third_queue_registration = RegistrationFactory(
        event=event_with_priority_pool, user=user_in_priority_pool
    )

    assert not registration.is_on_wait
    assert not first_queue_registration.is_on_wait
    assert not second_queue_registration.is_on_wait
    assert not third_queue_registration.is_on_wait
    assert event_with_priority_pool.waiting_list_count == 0

    client = get_api_client(user=admin_user)
    url = get_events_url_detail(event_with_priority_pool)
    data = get_event_data(limit=1)

    response = client.put(url, data)
    event_with_priority_pool.refresh_from_db()
    registration.refresh_from_db()
    first_queue_registration.refresh_from_db()
    second_queue_registration.refresh_from_db()
    third_queue_registration.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert event_with_priority_pool.limit == 1
    assert event_with_priority_pool.waiting_list_count == 3
    assert registration.is_on_wait
    assert first_queue_registration.is_on_wait
    assert second_queue_registration.is_on_wait
    assert not third_queue_registration.is_on_wait


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
def test_create_event_as_admin(permission_test_util):
    """
    HS and Index members should be able to create events no matter which organizer is selected.
    Other subgroup members can create events where event.organizer is their group or None.
    Leaders of committees and interest groups should be able to
    update events where event.organizer is their group or None.
    """

    (
        user,
        _,
        new_organizer,
        _,
        expected_status_code,
        _,
        _,
    ) = permission_test_util

    client = get_api_client(user=user)
    data = get_event_data(organizer=new_organizer)

    response = client.post(API_EVENTS_BASE_URL, data)

    assert (
        response.status_code == 201
        if expected_status_code == 200
        else expected_status_code
    )


@pytest.mark.django_db
@permission_params
def test_create_event_as_admin_with_contact_person(permission_test_util):
    """
    HS and Index members should be able to create events no matter which organizer is selected.
    They should also be able to create events no matter which contact person is selected.
    Other subgroup members can create events where event.organizer is their group or None.
    Leaders of committees and interest groups should be able to
    update events where event.organizer is their group or None.
    """

    (
        user,
        _,
        new_organizer,
        _,
        expected_status_code,
        _,
        _,
    ) = permission_test_util

    client = get_api_client(user=user)
    data = get_event_data(organizer=new_organizer, contact_person=user.user_id)
    response = client.post(API_EVENTS_BASE_URL, data)

    assert (
        response.status_code == 201
        if expected_status_code == 200
        else expected_status_code
    )


@pytest.mark.django_db
def test_create_event_with_group_priorities_returns_http_201(api_client, admin_user):
    client = api_client(user=admin_user)
    data = get_event_data()

    groups = GroupFactory.create_batch(2)
    groups = [group.slug for group in groups]
    data["priority_pools"] = [{"groups": groups}]

    response = client.post(API_EVENTS_BASE_URL, data)

    assert response.status_code == 201


@pytest.mark.django_db
def test_create_event_with_group_priorities_creates_the_priority_pools(
    api_client, admin_user
):
    client = api_client(user=admin_user)
    data = get_event_data()

    groups = GroupFactory.create_batch(2)
    groups_data = [group.slug for group in groups]
    data["priority_pools"] = [{"groups": groups_data}]

    response = client.post(API_EVENTS_BASE_URL, data)

    event_id = response.json().get("id")
    event = Event.objects.get(id=event_id)

    assert event.priority_pools.count() == 1
    assert all(
        actual == expected
        for actual, expected in zip(event.priority_pools.first().groups.all(), groups)
    )


@pytest.mark.django_db
def test_create_event_with_group_priorities_returns_priority_pools_in_response(
    api_client, admin_user
):
    client = api_client(user=admin_user)
    data = get_event_data()

    batch_size = 2
    groups = GroupFactory.create_batch(batch_size)
    group_slugs = [group.slug for group in groups]
    data["priority_pools"] = [{"groups": group_slugs}]

    response = client.post(API_EVENTS_BASE_URL, data)

    priority_pools = response.json().get("priority_pools")
    actual_groups = priority_pools[0].get("groups")

    assert len(priority_pools) == 1
    assert len(actual_groups) == batch_size
    assert all(group.get("slug") in group_slugs for group in actual_groups)


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
        (AdminGroup.PROMO, GroupType.SUBGROUP, MembershipType.MEMBER, 9),
        (AdminGroup.NOK, GroupType.SUBGROUP, MembershipType.MEMBER, 3),
        (AdminGroup.SOSIALEN, GroupType.SUBGROUP, MembershipType.MEMBER, 2),
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

    url = f"{API_EVENTS_BASE_URL}admin/"
    response = client.get(url)

    if expected_events_amount > 0:
        assert int(response.json().get("count")) == expected_events_amount
    else:
        assert response.status_code == 403


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


@pytest.mark.django_db
def test_list_public_registrations_anonymizes_correctly(member, api_client, event):
    """Should list user_info=None if user.public_event_registrations=False."""
    user1 = UserFactory(public_event_registrations=True)
    user2 = UserFactory(public_event_registrations=False)

    RegistrationFactory(event=event, user=user1)
    RegistrationFactory(event=event, user=user2)

    url = f"{get_events_url_detail(event)}public_registrations/"
    client = api_client(user=member)
    response = client.get(url)
    results = response.json().get("results")

    assert len(results) == 2
    assert results[0]["user_info"]["user_id"] == user1.user_id
    assert results[1]["user_info"] is None


@pytest.mark.django_db
def test_list_public_registrations_only_lists_not_on_wait(member, api_client):
    """Should only list registrations which is not on waitlist"""
    event = EventFactory(limit=1)
    user1 = UserFactory()
    user2 = UserFactory()
    RegistrationFactory(event=event, user=user1)
    RegistrationFactory(event=event, user=user2)

    url = f"{get_events_url_detail(event)}public_registrations/"
    client = api_client(user=member)
    response = client.get(url)
    results = response.json().get("results")

    assert len(results) == 1


@pytest.mark.django_db
def test_anonymous_list_public_registrations(api_client, event):
    """Anonymous users should not be able to list public registrations."""
    user1 = UserFactory(public_event_registrations=True)
    user2 = UserFactory(public_event_registrations=False)

    RegistrationFactory(event=event, user=user1)
    RegistrationFactory(event=event, user=user2)

    url = f"{get_events_url_detail(event)}public_registrations/"
    client = api_client()
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_expired_event_as_admin(api_client, admin_user):
    two_days_ago = now() - timedelta(days=1)
    event = EventFactory(end_date=two_days_ago)

    client = api_client(user=admin_user)
    url = get_events_url_detail(event)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_is_favorite_event_when_is_not_favorite(api_client, member, event):
    client = api_client(user=member)
    url = f"{get_events_url_detail(event)}favorite/"
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert not response.json().get("is_favorite")


@pytest.mark.django_db
def test_update_is_favorite_event_to_is_favorite(api_client, member, event):
    client = api_client(user=member)
    url = f"{get_events_url_detail(event)}favorite/"
    response = client.put(url, {"is_favorite": True})

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("is_favorite")


@pytest.mark.django_db
def test_update_is_favorite_event_to_is_not_favorite(api_client, member, event):
    event.favorite_users.add(member)

    client = api_client(user=member)
    url = f"{get_events_url_detail(event)}favorite/"
    response = client.put(url, {"is_favorite": False})

    assert response.status_code == status.HTTP_200_OK
    assert not response.json().get("is_favorite")


@pytest.mark.django_db
def test_retrieve_is_favorite_event_when_is_favorite(api_client, member, event):
    event.favorite_users.add(member)

    client = api_client(user=member)
    url = f"{get_events_url_detail(event)}favorite/"
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("is_favorite")


@pytest.mark.parametrize(
    ("user_favorite", "expected_count"),
    [
        [True, 1],
        [False, 3],
    ],
)
@pytest.mark.django_db
def test_user_favorite_filter_list(
    api_client, member, event, user_favorite, expected_count
):
    event.favorite_users.add(member)
    EventFactory.create_batch(2)

    client = api_client(user=member)
    url = f"{API_EVENTS_BASE_URL}?user_favorite={user_favorite}"
    response = client.get(url)

    actual_count = response.json().get("count")

    assert actual_count == expected_count


@pytest.mark.parametrize(
    ("expired", "expected_count"),
    [
        [True, 1],
        [False, 2],
    ],
)
@pytest.mark.django_db
def test_expired_filter_list(api_client, admin_user, expired, expected_count):
    two_days_ago = now() - timedelta(days=1)
    tomorrow = now() + timedelta(days=1)
    EventFactory(end_date=two_days_ago)
    EventFactory.create_batch(2, end_date=tomorrow)

    client = api_client(user=admin_user)
    url = f"{API_EVENTS_BASE_URL}admin/?expired={expired}"
    response = client.get(url)

    actual_count = response.json().get("count")

    assert actual_count == expected_count


@pytest.mark.django_db
def test_jubkom_has_create_permission(api_client, jubkom_member):
    client = api_client(user=jubkom_member)
    organizer = Group.objects.get(name=Groups.JUBKOM).slug
    data = get_event_data(organizer=organizer)
    response = client.post(API_EVENTS_BASE_URL, data)

    assert response.status_code == status.HTTP_201_CREATED
