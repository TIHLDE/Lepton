from datetime import timedelta

from rest_framework import status

import pytest

from app.common.enums import AdminGroup, Groups
from app.common.enums import NativeGroupType as GroupType
from app.common.enums import NativeMembershipType as MembershipType
from app.common.enums import NativeUserStudy as StudyType
from app.content.factories import EventFactory, RegistrationFactory, UserFactory
from app.content.factories.priority_pool_factory import PriorityPoolFactory
from app.forms.enums import NativeEventFormType as EventFormType
from app.forms.tests.form_factories import EventFormFactory, SubmissionFactory
from app.group.factories import GroupFactory
from app.payment.enums import OrderStatus
from app.payment.factories import OrderFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client
from app.util.utils import now

API_EVENT_BASE_URL = "/events/"


def _get_registration_url(event):
    return f"{API_EVENT_BASE_URL}{event.pk}/registrations/"


def _get_registration_detail_url(registration):
    return f"{_get_registration_url(registration.event)}{registration.user.user_id}/"


# "event_organizer" should have one of 3 different values:
# - None -> The event has no connected organizer
# - "same" -> The event is connected to same organizer as user is member of
# - "other" -> The event is connected to another organizer as user i member of
permission_params = pytest.mark.parametrize(
    (
        "organizer_name",
        "organizer_type",
        "membership_type",
        "expected_status_code",
        "event_organizer",
    ),
    (
        [AdminGroup.HS, GroupType.BOARD, MembershipType.MEMBER, 200, "same"],
        [AdminGroup.HS, GroupType.BOARD, MembershipType.MEMBER, 200, "other"],
        [AdminGroup.HS, GroupType.BOARD, MembershipType.MEMBER, 200, None],
        [AdminGroup.INDEX, GroupType.SUBGROUP, MembershipType.MEMBER, 200, "same"],
        [AdminGroup.INDEX, GroupType.SUBGROUP, MembershipType.MEMBER, 200, "other"],
        [AdminGroup.INDEX, GroupType.SUBGROUP, MembershipType.MEMBER, 200, None],
        [AdminGroup.NOK, GroupType.SUBGROUP, MembershipType.MEMBER, 200, "same"],
        [AdminGroup.NOK, GroupType.SUBGROUP, MembershipType.MEMBER, 403, "other"],
        [AdminGroup.NOK, GroupType.SUBGROUP, MembershipType.MEMBER, 200, None],
        ["KontKom", GroupType.COMMITTEE, MembershipType.LEADER, 200, "same"],
        ["Pythons", GroupType.INTERESTGROUP, MembershipType.LEADER, 200, "same"],
        ["KontKom", GroupType.COMMITTEE, MembershipType.LEADER, 200, None],
        ["Pythons", GroupType.INTERESTGROUP, MembershipType.LEADER, 200, None],
        ["KontKom", GroupType.COMMITTEE, MembershipType.LEADER, 403, "other"],
        ["Pythons", GroupType.INTERESTGROUP, MembershipType.LEADER, 403, "other"],
        ["KontKom", GroupType.COMMITTEE, MembershipType.MEMBER, 403, "same"],
        ["Pythons", GroupType.INTERESTGROUP, MembershipType.MEMBER, 403, "same"],
    ),
)


@pytest.fixture
@permission_params
def permission_test_util(
    member,
    organizer_name,
    organizer_type,
    membership_type,
    expected_status_code,
    event_organizer,
):
    organizer = add_user_to_group_with_name(
        member, organizer_name, organizer_type, membership_type
    )
    if event_organizer == "same":
        event_organizer = organizer
    elif event_organizer == "other":
        event_organizer = GroupFactory()
    event = EventFactory(organizer=event_organizer)
    registration = RegistrationFactory(event=event)
    return member, registration, event_organizer, expected_status_code


def _get_registration_post_data(user, event):
    return {
        "user_id": user.user_id,
        "event": event.pk,
    }


def _get_registration_put_data(user, event):
    return {
        **_get_registration_post_data(user, event),
        "is_on_wait": False,
        "has_attended": False,
    }


@pytest.mark.django_db
def test_list_as_anonymous_user(default_client, event):
    """An anonymous user should not be able to list all registrations for an event."""
    url = _get_registration_url(event)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_as_member(member, registration):
    """A member should not be able to list all registrations for an event."""
    client = get_api_client(user=member)
    url = _get_registration_url(registration.event)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@permission_params
def test_list_as_member_in_organizer(permission_test_util):
    """
    A member of HS or Index should be able to list all registrations.
    A member of subgroup or leader of committee and interest groups should be able to
    list all registrations for an event that has event.organizer None or equal the same group.
    """
    member, registration, event_organizer, expected_status_code = permission_test_util
    client = get_api_client(user=member)
    url = _get_registration_url(registration.event)
    response = client.get(url)

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert len(response.json()) > 0
        assert response.json()["results"][0]["user_info"]


@pytest.mark.django_db
def test_retrieve_as_anonymous_user(default_client, registration):
    """An anonymous user should not be able to retrieve a single registration for an event."""
    url = _get_registration_detail_url(registration)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_as_member(member):
    """A member should be able to retrieve their own registration for an event."""
    registration = RegistrationFactory(user=member)
    client = get_api_client(user=member)

    url = _get_registration_detail_url(registration)
    response = client.get(url)
    actual_user_id = response.json().get("user_info").get("user_id")

    assert response.status_code == status.HTTP_200_OK
    assert actual_user_id == member.user_id


@pytest.mark.django_db
def test_retrieve_another_registration_as_member(member, registration):
    """A member should not be able to retrieve any other registrations for an event."""
    client = get_api_client(user=member)
    url = _get_registration_detail_url(registration)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@permission_params
def test_retrieve_as_member_in_organizer(permission_test_util):
    """
    A member of HS or Index should be able to retrieve any registration.
    A member of subgroup or leader of committee and interest groups should be able to
    retrieve any registration for an event that has event.organizer None or equal the same group.
    """
    member, registration, event_organizer, expected_status_code = permission_test_util
    client = get_api_client(user=member)
    url = _get_registration_detail_url(registration)
    response = client.get(url)

    assert response.status_code == expected_status_code
    assert len(response.json()) > 0


@pytest.mark.django_db
def test_retrieve_when_not_found(user):
    """Should return a status code of status.HTTP_404_NOT_FOUND."""
    client = get_api_client(user=user, group_name=AdminGroup.HS)
    url = _get_registration_url(EventFactory()) + "notFound/"
    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_as_anonymous_user(default_client, user, event):
    """An anonymous user should not be able to create a registration."""
    data = _get_registration_post_data(user, event)
    url = _get_registration_url(event=event)
    response = default_client.post(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_as_member_registers_themselves(member, event):
    """A member should be able to create a registration for themselves."""
    data = _get_registration_post_data(member, event)
    client = get_api_client(user=member)

    url = _get_registration_url(event=event)
    response = client.post(url, data=data)

    actual_user_id = response.json().get("user_info").get("user_id")

    assert response.status_code == status.HTTP_201_CREATED
    assert actual_user_id == member.user_id


@pytest.mark.django_db
def test_create_as_member_registers_themselves_not_accept_rules(member, event):
    """A member should not be able to create a registration for themselves without accepting rules."""
    member.accepts_event_rules = False
    member.save()

    data = _get_registration_post_data(member, event)
    client = get_api_client(user=member)

    url = _get_registration_url(event=event)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_as_member_registers_themselves_not_allow_photo(member, event):
    """A member should be able to create a registration and not allow photo."""
    member.allows_photo_by_default = False
    member.save()
    data = _get_registration_post_data(member, event)
    client = get_api_client(user=member)

    url = _get_registration_url(event=event)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert not response.json().get("allow_photo")


@pytest.mark.django_db
def test_create_as_member_for_someone_else_registers_themselves(member, user, event):
    """
    A member should not be able to create a registration for anyone else than themselves.
    A registration for this member should instead be created.
    """
    data = _get_registration_post_data(user, event)
    client = get_api_client(user=member)

    url = _get_registration_url(event=event)
    response = client.post(url, data=data)

    actual_user_id = response.json().get("user_info").get("user_id")

    assert response.status_code == status.HTTP_201_CREATED
    assert actual_user_id == member.user_id


@pytest.mark.django_db
def test_create_as_admin_registers_themselves(admin_user, member, event):
    """
    An admin should not be able to create a registration for anyone else than themselves.
    A registration for this member should instead be created.
    """
    data = _get_registration_post_data(member, event)
    client = get_api_client(user=admin_user)

    url = _get_registration_url(event=event)
    response = client.post(url, data=data)

    actual_user_id = response.json().get("user_info").get("user_id")

    assert response.status_code == status.HTTP_201_CREATED
    assert actual_user_id == admin_user.user_id


@pytest.mark.django_db
def test_create_when_event_not_found(admin_user, member):
    """Should return a status code of status.HTTP_404_NOT_FOUND."""
    unsaved_event = EventFactory.build(pk=-1)
    data = _get_registration_post_data(member, unsaved_event)

    client = get_api_client(user=admin_user)
    url = _get_registration_url(event=unsaved_event)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_as_member_when_event_is_closed(member):
    """A registration is not possible if the event is closed."""
    closed_event = EventFactory(closed=True)
    data = _get_registration_post_data(member, closed_event)

    client = get_api_client(user=member)
    url = _get_registration_url(event=closed_event)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_another_registration_as_admin_when_event_is_closed(admin_user, member):
    """A registration is not possible if the event is closed."""
    closed_event = EventFactory(closed=True)
    data = _get_registration_post_data(member, closed_event)

    client = get_api_client(user=admin_user)
    url = _get_registration_url(event=closed_event)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_when_event_does_not_have_signup(admin_user, member):
    """A registration is not possible if the event has not enabled sign up."""
    event_without_sign_up = EventFactory(sign_up=False)
    data = _get_registration_post_data(member, event_without_sign_up)
    client = get_api_client(user=admin_user)
    url = _get_registration_url(event=event_without_sign_up)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_when_event_registration_has_not_started(admin_user, member):
    """A registration is not possible if the events registration has not started."""
    tomorrow = now() + timedelta(days=1)
    event_registration_not_started = EventFactory(start_registration_at=tomorrow)
    data = _get_registration_post_data(member, event_registration_not_started)

    client = get_api_client(user=admin_user)
    url = _get_registration_url(event=event_registration_not_started)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_when_event_registration_has_ended(admin_user, member):
    """A registration is not possible if the events registration has ended."""
    yesterday = now() - timedelta(days=1)
    event_registration_not_started = EventFactory(end_registration_at=yesterday)
    data = _get_registration_post_data(member, event_registration_not_started)

    client = get_api_client(user=admin_user)
    url = _get_registration_url(event=event_registration_not_started)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_when_event_not_found(member):
    """Should return a status code of status.HTTP_404_NOT_FOUND."""
    unsaved_event = EventFactory.build(pk=-1)
    data = _get_registration_put_data(member, unsaved_event)

    client = get_api_client(user=member)
    url = _get_registration_url(event=unsaved_event)
    response = client.put(url, data=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_update_as_anonymous_user(default_client, registration):
    """An anonymous user should not be able to update a registration."""
    url = _get_registration_detail_url(registration)
    response = default_client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_member(member):
    """A member should not be able to update a registration."""
    registration_to_update = RegistrationFactory(user=member)
    event = registration_to_update.event
    data = _get_registration_put_data(user=member, event=event)

    client = get_api_client(user=member)
    url = _get_registration_detail_url(registration_to_update)
    response = client.put(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_own_registration_as_admin(admin_user):
    """An admin user should be able to update their own registration."""
    registration_to_update = RegistrationFactory(user=admin_user)
    data = _get_registration_put_data(
        user=admin_user, event=registration_to_update.event
    )

    is_on_wait_negated = not registration_to_update.is_on_wait
    data["is_on_wait"] = is_on_wait_negated

    client = get_api_client(user=admin_user)
    url = _get_registration_detail_url(registration_to_update)
    response = client.put(url, data=data)

    actual_user_id = response.json().get("user_info").get("user_id")
    updated_is_on_wait = response.json().get("is_on_wait")

    assert response.status_code == status.HTTP_200_OK
    assert actual_user_id == admin_user.user_id
    assert not updated_is_on_wait == registration_to_update.is_on_wait


@pytest.mark.django_db
def test_update_registration_updated_fields(admin_user):
    """An update should actually update the registration."""
    registration_to_update = RegistrationFactory(user=admin_user)
    data = _get_registration_put_data(
        user=admin_user, event=registration_to_update.event
    )

    is_on_wait_negated = not registration_to_update.is_on_wait
    data["is_on_wait"] = is_on_wait_negated

    client = get_api_client(user=admin_user)
    url = _get_registration_detail_url(registration_to_update)
    response = client.put(url, data=data)

    registration_to_update.refresh_from_db()

    updated_is_on_wait = response.json().get("is_on_wait")

    assert updated_is_on_wait == registration_to_update.is_on_wait


@pytest.mark.django_db
@permission_params
def test_update_another_registration_as_admin(permission_test_util):
    """An admin user should be able to update any registration."""
    (
        member,
        registration_to_update,
        event_organizer,
        expected_status_code,
    ) = permission_test_util
    data = _get_registration_put_data(user=member, event=registration_to_update.event)

    is_on_wait_negated = not registration_to_update.is_on_wait
    data["is_on_wait"] = is_on_wait_negated

    client = get_api_client(user=member)
    url = _get_registration_detail_url(registration_to_update)
    response = client.put(url, data=data)

    updated_is_on_wait = response.json().get("is_on_wait")

    assert response.status_code == expected_status_code
    assert not updated_is_on_wait == registration_to_update.is_on_wait


@pytest.mark.django_db
def test_bump_another_registration_as_admin_when_event_is_full_is_not_allowed(
    admin_user,
):
    """An admin user should not be able to move registration up from the waiting list when the event is full."""
    event = EventFactory(limit=1)
    RegistrationFactory(event=event)

    assert event.is_full

    registration_to_update = RegistrationFactory(event=event)

    assert registration_to_update.is_on_wait

    data = _get_registration_put_data(
        user=admin_user, event=registration_to_update.event
    )

    data["is_on_wait"] = False

    client = get_api_client(user=admin_user)
    url = _get_registration_detail_url(registration_to_update)
    response = client.put(url, data=data)

    registration_to_update.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert registration_to_update.is_on_wait


@pytest.mark.django_db
def test_new_registration_on_full_event_goes_to_wait(member):
    """Tests if a new registation on a full event goes to waiting list"""
    event = EventFactory(limit=1)
    RegistrationFactory(event=event)

    assert event.is_full

    data = _get_registration_post_data(member, event)

    client = get_api_client(user=member)
    url = _get_registration_url(event=event)
    response = client.post(url, data=data)

    actual_registration = event.registrations.get(user=member)

    assert response.status_code == status.HTTP_201_CREATED
    assert actual_registration.is_on_wait


@pytest.mark.django_db
def test_update_when_registration_not_found(admin_user, member, event):
    """Should return a status code of status.HTTP_404_NOT_FOUND."""
    unsaved_registration = RegistrationFactory.build(user=member, event=event)
    data = _get_registration_put_data(user=admin_user, event=unsaved_registration.event)

    client = get_api_client(user=admin_user)
    url = _get_registration_detail_url(unsaved_registration)
    response = client.put(url, data=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_update_when_user_not_found(admin_user, registration):
    """Should return a status code of status.HTTP_404_NOT_FOUND."""
    data = _get_registration_put_data(user=admin_user, event=registration.event)

    client = get_api_client(user=admin_user)
    url = _get_registration_url(registration.event) + "notFound/"
    response = client.put(url, data=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_update_fails_when_user_has_attended(admin_user):
    """
    It should not be possible to update a registration
    if the user has attended.
    """
    registration_to_update = RegistrationFactory(has_attended=True)
    data = _get_registration_put_data(
        user=admin_user, event=registration_to_update.event
    )
    data["has_attended"] = True

    client = get_api_client(user=admin_user)
    url = _get_registration_detail_url(registration_to_update)
    response = client.put(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_returns_a_single_registration_when_user_has_multiple_for_different_events(
    member, admin_user
):
    """
    Test that a single registration is returned even
    if the user has multiple registrations for different events.
    """
    RegistrationFactory.create_batch(4, user=member)

    registration_to_update = RegistrationFactory(user=member)
    event = registration_to_update.event
    data = _get_registration_put_data(user=member, event=event)

    client = get_api_client(user=admin_user)
    url = _get_registration_detail_url(registration_to_update)
    response = client.put(url, data=data)

    actual_user_id = response.json().get("user_info").get("user_id")

    assert actual_user_id == member.user_id


@pytest.mark.django_db
def test_delete_when_not_found(admin_user):
    """Should return a status code of status.HTTP_404_NOT_FOUND."""
    client = get_api_client(user=admin_user)
    url = _get_registration_url(EventFactory()) + "notFound/"
    response = client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_as_anonymous(default_client, registration):
    """An anonymous user should not be able to delete any registrations."""
    url = _get_registration_detail_url(registration)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_own_registration_as_member(member):
    """A member should only be able to delete their own registration."""
    registration = RegistrationFactory(user=member)
    client = get_api_client(user=member)

    url = _get_registration_detail_url(registration)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_another_registration_as_member(member, user):
    """A member should not be able to delete another registration."""
    registration = RegistrationFactory(user=user)
    client = get_api_client(user=member)

    url = _get_registration_detail_url(registration)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_as_member_when_sign_off_deadline_has_passed_and_not_on_wait(member):
    """
    A member should be able to delete their registration
    when the events sign off deadline has passed and is not on wait within one hour.
    """
    event = EventFactory(sign_off_deadline=now() - timedelta(days=1), limit=10)
    registration = RegistrationFactory(user=member, event=event, is_on_wait=False)
    client = get_api_client(user=member)

    url = _get_registration_detail_url(registration)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_as_member_when_sign_off_deadline_has_passed_and_on_wait(member):
    """
    A member should be able to delete their registration
    when the events sign off deadline has passed but is on wait.
    """
    event = EventFactory(sign_off_deadline=now() - timedelta(days=1))
    registration = RegistrationFactory(user=member, event=event)
    client = get_api_client(user=member)

    url = _get_registration_detail_url(registration)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    "organizer_name",
    [
        AdminGroup.PROMO,
        AdminGroup.NOK,
        AdminGroup.KOK,
        AdminGroup.SOSIALEN,
        AdminGroup.INDEX,
    ],
)
def test_delete_another_registration_as_member_in_nok_or_promo(
    member, organizer_name, user
):
    """A member of NOK, PROMO, Sosialen or KOK should be able to delete another registration for an event."""
    registration = RegistrationFactory(user=user)
    client = get_api_client(user=member, group_name=organizer_name)
    response = client.delete(_get_registration_detail_url(registration))

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_another_registration_as_admin(admin_user, member):
    """An admin user should be able to delete any registration."""
    registration = RegistrationFactory(user=member)
    client = get_api_client(user=admin_user)

    url = _get_registration_detail_url(registration)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_another_registration_as_admin_after_sign_off_deadline(
    admin_user, member
):
    """An admin user should be able to delete any registration after sign off deadline."""
    event = EventFactory(sign_off_deadline=now() - timedelta(days=1))
    registration = RegistrationFactory(user=member, event=event)
    client = get_api_client(user=admin_user)

    url = _get_registration_detail_url(registration)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_own_registration_as_admin_bumps_first_user_on_wait(admin_user):
    """
    Test that the first registration on the waiting list is moved up
    when an admin deletes their own registration
    """
    event = EventFactory(limit=1)
    admin_registration = RegistrationFactory(event=event, user=admin_user)
    registration_on_wait = RegistrationFactory(event=event)

    client = get_api_client(user=admin_user)
    url = _get_registration_detail_url(admin_registration)
    client.delete(url)

    registration_on_wait.refresh_from_db()

    assert not registration_on_wait.is_on_wait


@pytest.mark.django_db
def test_delete_own_registration_as_member_when_no_users_on_wait_are_in_a_priority_pool_bumps_first_registration_on_wait(
    member,
):
    """
    Test that the first registration on wait is moved up when
    a member deletes their own registration and the event has no priorities.
    """
    event = EventFactory(limit=1)
    PriorityPoolFactory(event=event, groups=(GroupFactory(),))

    user_not_in_priority_pool = UserFactory()

    registration_to_delete = RegistrationFactory(event=event, user=member)
    registration_on_wait = RegistrationFactory(
        event=event, user=user_not_in_priority_pool
    )

    client = get_api_client(user=member)
    url = _get_registration_detail_url(registration_to_delete)
    client.delete(url)

    registration_on_wait.refresh_from_db()

    assert not registration_on_wait.is_on_wait


@pytest.mark.django_db
def test_that_users_cannot_register_when_has_unanswered_evaluations(api_client, user):
    evaluation = EventFormFactory(type=EventFormType.EVALUATION)
    RegistrationFactory(event=evaluation.event, user=user, has_attended=True)

    next_event = EventFactory()

    data = _get_registration_post_data(user, next_event)
    url = _get_registration_url(event=next_event)
    response = api_client(user=user).post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not next_event.registrations.filter(user=user).exists()


@pytest.mark.django_db
def test_that_users_can_register_when_has_unanswered_evaluation_over_20_days(
    api_client, user
):
    date_30_days_ago = now() - timedelta(days=30)
    event = EventFactory(end_date=date_30_days_ago)
    evaluation = EventFormFactory(type=EventFormType.EVALUATION, event=event)
    RegistrationFactory(event=evaluation.event, user=user, has_attended=True)

    next_event = EventFactory()

    data = _get_registration_post_data(user, next_event)
    url = _get_registration_url(event=next_event)
    response = api_client(user=user).post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert next_event.registrations.filter(user=user).exists()


@pytest.mark.django_db
def test_that_users_can_register_when_has_no_unanswered_evaluations(api_client, user):
    evaluation = EventFormFactory(type=EventFormType.EVALUATION)
    RegistrationFactory(event=evaluation.event, user=user, has_attended=True)
    SubmissionFactory(form=evaluation, user=user)

    next_event = EventFactory()

    data = _get_registration_post_data(user, next_event)
    url = _get_registration_url(event=next_event)
    response = api_client(user=user).post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert next_event.registrations.filter(user=user).exists()


@pytest.mark.django_db
def test_add_registration_to_event_as_admin(api_client, admin_user, event):
    """
    An admin should be able to add a registration to an event
    manually.
    """

    data = {"user": admin_user.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    response = api_client(user=admin_user).post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_add_registration_to_event_as_admin_when_event_is_full(
    api_client, admin_user, member, event
):
    """
    An admin should be able to add a registration to an event
    manually. If the event is full, the member should be added to the waiting list.
    """

    event.limit = 1
    event.save()
    registration = RegistrationFactory(event=event)

    assert not registration.is_on_wait

    data = {"user": member.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    response = api_client(user=admin_user).post(url, data=data)

    event.refresh_from_db()

    assert response.status_code == status.HTTP_201_CREATED
    assert event.registrations.get(user=member).is_on_wait


@pytest.mark.django_db
@pytest.mark.parametrize(
    "organizer_name",
    [
        AdminGroup.PROMO,
        AdminGroup.NOK,
        AdminGroup.KOK,
        AdminGroup.SOSIALEN,
        AdminGroup.INDEX,
    ],
)
def test_add_registration_to_event_as_admin_group_member(event, member, organizer_name):
    """
    A member of NOK, Promo, Sosialen or KOK should be able to add a
    registration to an event manually.
    """

    data = {"user": member.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    client = get_api_client(user=member, group_name=organizer_name)

    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "organizer_name",
    [
        AdminGroup.PROMO,
        AdminGroup.NOK,
        AdminGroup.KOK,
        AdminGroup.SOSIALEN,
        AdminGroup.INDEX,
    ],
)
def test_add_existing_user_registration_to_event_as_admin_group_member(
    event, member, organizer_name
):
    """
    A member of NOK, Promo, Sosialen or KOK should not be able to add a registration
    to an event manually if the user is already registered.
    """

    RegistrationFactory(event=event, user=member)

    data = {"user": member.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    client = get_api_client(user=member, group_name=organizer_name)

    response = client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize(
    "organizer_name",
    [
        AdminGroup.PROMO,
        AdminGroup.NOK,
        AdminGroup.KOK,
        AdminGroup.SOSIALEN,
        AdminGroup.INDEX,
    ],
)
def test_add_registration_to_event_as_admin_group_member_when_event_closed(
    event, member, organizer_name
):
    """
    A member of NOK, Promo, Sosialen or KOK should be able to add a
    registration to an event manually even though the event is closed.
    """

    event.closed = True
    event.save()

    data = {"user": member.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    client = get_api_client(user=member, group_name=organizer_name)

    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "organizer_name",
    [
        AdminGroup.PROMO,
        AdminGroup.NOK,
        AdminGroup.KOK,
        AdminGroup.SOSIALEN,
        AdminGroup.INDEX,
    ],
)
def test_add_registration_to_event_as_admin_group_member_before_registration_open(
    event, member, organizer_name
):
    """
    A member of NOK, Promo, Sosialen or KOK should be able to add a
    registration to an event manually even though the registration has not opened.
    """

    event.start_registration_at = now() + timedelta(days=1)
    event.save()

    data = {"user": member.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    client = get_api_client(user=member, group_name=organizer_name)

    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "organizer_name",
    [
        AdminGroup.PROMO,
        AdminGroup.NOK,
        AdminGroup.KOK,
        AdminGroup.SOSIALEN,
        AdminGroup.INDEX,
    ],
)
def test_add_registration_to_event_as_admin_group_member_after_registration_closed(
    event, member, organizer_name
):
    """
    A member of NOK, Promo, Sosialen or KOK should be able to add a
    registration to an event manually even though the registration has closed.
    """

    event.end_registration_at = now() - timedelta(days=1)
    event.save()

    data = {"user": member.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    client = get_api_client(user=member, group_name=organizer_name)

    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_add_registration_to_event_as_anonymous_user(default_client, event, member):
    """
    An anonymous user should not be able to add a registration to an
    event manually.
    """

    data = {"user": member.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    response = default_client.post(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_add_registration_to_event_as_member(member, event):
    """
    A member should not be able to add a registration to an
    event manually.
    """

    data = {"user": member.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    client = get_api_client(user=member)

    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name",
    [
        Groups.JUBKOM,
        Groups.REDAKSJONEN,
        Groups.FONDET,
        Groups.PLASK,
        Groups.DRIFT,
    ],
)
def test_add_registration_to_event_as_group_member(event, member, group_name):
    """
    A member of a specific group (not part of AdminGroup) should be able to add a
    registration to an event if their group organized it.
    """

    member_group = add_user_to_group_with_name(
        member, group_name, GroupType.SUBGROUP, MembershipType.MEMBER
    )

    event.organizer = member_group
    event.save()

    data = {"user": member.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    client = get_api_client(user=member)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name",
    [
        Groups.JUBKOM,
        Groups.REDAKSJONEN,
        Groups.FONDET,
        Groups.PLASK,
        Groups.DRIFT,
    ],
)
def test_add_registration_to_event_as_group_member_of_non_organizing_group(
    event, member, group_name
):
    """
    A member of a specific group (not part of AdminGroup) should NOT be able to add a
    registration to an event if their group did not organize it.
    """
    add_user_to_group_with_name(
        member, group_name, GroupType.SUBGROUP, MembershipType.MEMBER
    )

    event.organizer = GroupFactory(name="Different Organizer")
    event.save()

    data = {"user": member.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    client = get_api_client(user=member)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name",
    [
        Groups.JUBKOM,
        Groups.REDAKSJONEN,
        Groups.FONDET,
        Groups.PLASK,
        Groups.DRIFT,
    ],
)
def test_add_registration_when_event_is_full(event, member, group_name):
    """
    A member of the organizing group should be able to add a registration to an event
    for another member even when the event is full, and the registration should be added to the waitlist.
    """

    member_group = add_user_to_group_with_name(
        member, group_name, GroupType.SUBGROUP, MembershipType.MEMBER
    )

    event.organizer = member_group
    event.limit = 1
    event.save()

    RegistrationFactory(event=event)

    data = {"user": member.user_id, "event": event.id}
    url = f"{_get_registration_url(event=event)}add/"

    client = get_api_client(user=member)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert event.registrations.get(user=member).is_on_wait


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("order_status", "status_code"),
    [
        (OrderStatus.SALE, status.HTTP_400_BAD_REQUEST),
        (OrderStatus.CAPTURE, status.HTTP_400_BAD_REQUEST),
        (OrderStatus.RESERVED, status.HTTP_400_BAD_REQUEST),
        (OrderStatus.CANCEL, status.HTTP_200_OK),
        (OrderStatus.INITIATE, status.HTTP_200_OK),
        (OrderStatus.REFUND, status.HTTP_200_OK),
        (OrderStatus.VOID, status.HTTP_200_OK),
    ],
)
def test_delete_registration_with_paid_order_as_self(
    member, event, order, paid_event, order_status, status_code
):
    """
    A member should not be able to delete their registration if they have a paid order.
    """

    order.status = order_status
    order.event = event
    order.user = member
    order.save()

    paid_event.event = event
    paid_event.save()

    registration = RegistrationFactory(user=member, event=event)
    client = get_api_client(user=member)

    url = _get_registration_detail_url(registration)
    response = client.delete(url)

    assert response.status_code == status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("filter_params", "participant_count", "status_code"),
    [
        ({"has_allergy": True}, 2, status.HTTP_200_OK),
        ({"year": "2050"}, 1, status.HTTP_200_OK),
        ({"year": "2051"}, 1, status.HTTP_200_OK),
        ({"study": StudyType.DATAING}, 2, status.HTTP_200_OK),
        ({"year": "2050", "study": StudyType.DATAING}, 1, status.HTTP_200_OK),
        (
            {"has_allergy": True, "year": "2051", "study": StudyType.DATAING},
            1,
            status.HTTP_200_OK,
        ),
        (
            {"has_allergy": True, "year": "2050", "study": StudyType.DATAING},
            1,
            status.HTTP_200_OK,
        ),
    ],
)
def test_filter_participants(
    new_admin_user, member, event, filter_params, participant_count, status_code
):
    """
    An admin should be able to filter the participants of an event using multiple parameters
    """

    member.allergy = "Pizza"
    member.save()

    new_admin_user.allergy = "Fisk"
    new_admin_user.save()

    add_user_to_group_with_name(member, StudyType.DATAING, GroupType.STUDY)
    add_user_to_group_with_name(member, "2050", GroupType.STUDYYEAR)

    add_user_to_group_with_name(new_admin_user, "2051", GroupType.STUDYYEAR)
    add_user_to_group_with_name(new_admin_user, StudyType.DATAING, GroupType.STUDY)

    RegistrationFactory(user=member, event=event)
    RegistrationFactory(user=new_admin_user, event=event)
    client = get_api_client(user=new_admin_user)

    # Build the query string with multiple filter parameters
    url = (
        _get_registration_url(event)
        + "?"
        + "&".join([f"{key}={value}" for key, value in filter_params.items()])
    )
    response = client.get(url)

    assert participant_count == response.data["count"]
    assert response.status_code == status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("filter_params", "participant_count", "status_code"),
    [
        ({"study": StudyType.DATAING, "has_paid": True}, 1, status.HTTP_200_OK),
        ({"study": StudyType.DIGFOR, "has_paid": True}, 2, status.HTTP_200_OK),
        ({"study": StudyType.DIGFOR, "has_paid": False}, 1, status.HTTP_200_OK),
        ({"has_paid": True, "year": "2050"}, 1, status.HTTP_200_OK),
        ({"has_paid": True, "year": "2051"}, 1, status.HTTP_200_OK),
        ({"has_paid": True}, 4, status.HTTP_200_OK),
        ({"has_paid": False}, 2, status.HTTP_200_OK),
    ],
)
def test_filter_participants_paid_event(
    new_admin_user,
    member,
    event,
    paid_event,
    filter_params,
    participant_count,
    status_code,
):
    """
    An admin should be able to filter the participants of an event using multiple parameters
    """

    paid_event.event = event

    paid_event.save()

    member.allergy = "Pizza"
    member.save()

    new_admin_user.allergy = "Fisk"
    new_admin_user.save()

    new_user = UserFactory()
    new_user2 = UserFactory()
    new_user3 = UserFactory()
    new_user4 = UserFactory()

    add_user_to_group_with_name(member, StudyType.DATAING, GroupType.STUDY)
    add_user_to_group_with_name(member, "2050", GroupType.STUDYYEAR)

    add_user_to_group_with_name(new_admin_user, "2051", GroupType.STUDYYEAR)
    add_user_to_group_with_name(new_admin_user, StudyType.DIGFOR, GroupType.STUDY)
    add_user_to_group_with_name(new_user2, StudyType.DIGFOR, GroupType.STUDY)
    add_user_to_group_with_name(new_user3, StudyType.DIGFOR, GroupType.STUDY)

    RegistrationFactory(user=member, event=event)
    RegistrationFactory(user=new_admin_user, event=event)
    RegistrationFactory(user=new_user, event=event)
    RegistrationFactory(user=new_user2, event=event)
    RegistrationFactory(user=new_user3, event=event)
    RegistrationFactory(user=new_user4, event=event)

    OrderFactory(event=event, user=member, status=OrderStatus.SALE)
    OrderFactory(event=event, user=new_admin_user, status=OrderStatus.SALE)
    OrderFactory(event=event, user=new_user4, status=OrderStatus.SALE)
    OrderFactory(event=event, user=new_user2, status=OrderStatus.SALE)
    OrderFactory(event=event, user=new_user, status=OrderStatus.CANCEL)
    OrderFactory(event=event, user=new_user3, status=OrderStatus.CANCEL)

    client = get_api_client(user=new_admin_user)

    # Build the query string with multiple filter parameters
    url = (
        _get_registration_url(paid_event)
        + "?"
        + "&".join([f"{key}={value}" for key, value in filter_params.items()])
    )
    response = client.get(url)
    assert participant_count == response.data["count"]
    assert response.status_code == status_code
