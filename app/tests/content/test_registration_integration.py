from datetime import timedelta

from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.content.factories import EventFactory, RegistrationFactory
from app.util.test_utils import get_api_client
from app.util.utils import today

API_EVENT_BASE_URL = "/api/v1/events/"


def _get_registration_url(event):
    return f"{API_EVENT_BASE_URL}{event.pk}/users/"


def _get_registration_detail_url(registration):
    return f"{_get_registration_url(registration.event)}{registration.user.user_id}/"


def _get_registration_post_data(user, event):
    return {
        "user_id": user.user_id,
        "event": event.pk,
        "allow_photo": False,
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
@pytest.mark.parametrize(
    "group_name",
    [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.SOSIALEN, AdminGroup.NOK],
)
def test_list_as_member_in_hs_devkom_sosialen_or_nok(registration, member, group_name):
    """
    A member of HS, Devkom, Sosialen or NoK should
    be able to list all registrations for an event with info about users.
    """
    client = get_api_client(user=member, group_name=group_name)
    url = _get_registration_url(registration.event)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
    assert response.json()[0]["user_info"]


@pytest.mark.django_db
def test_list_as_member_in_promo(registration, member):
    """A member of PROMO should not be able to list all registrations for an event."""
    client = get_api_client(user=member, group_name=AdminGroup.PROMO)
    url = _get_registration_url(registration.event)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


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
@pytest.mark.parametrize(
    "group_name", [AdminGroup.HS, AdminGroup.INDEX,],
)
def test_retrieve_as_member_in_hs_or_devkom(registration, member, group_name):
    """A member of HS or Devkom should be able to retrieve any registration for an event."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_registration_detail_url(registration)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name", [AdminGroup.PROMO, AdminGroup.NOK,],
)
def test_retrieve_other_registrations_as_member_in_nok_or_promo(
    member, group_name, user
):
    """A member of NOK or PROMO should not be able to retrieve other registrations than themselves."""
    registration = RegistrationFactory(user=user)
    client = get_api_client(user=member, group_name=group_name)

    url = _get_registration_detail_url(registration)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


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
    tomorrow = today() + timedelta(days=1)
    event_registration_not_started = EventFactory(start_registration_at=tomorrow)
    data = _get_registration_post_data(member, event_registration_not_started)

    client = get_api_client(user=admin_user)
    url = _get_registration_url(event=event_registration_not_started)
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_when_event_registration_has_ended(admin_user, member):
    """A registration is not possible if the events registration has ended."""
    yesterday = today() - timedelta(days=1)
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
def test_update_another_registration_as_admin(admin_user, member):
    """An admin user should be able to update any registration."""
    registration_to_update = RegistrationFactory(user=member)
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
    assert actual_user_id == member.user_id
    assert not updated_is_on_wait == registration_to_update.is_on_wait


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
def test_delete_as_member_when_sign_off_deadline_has_passed(member):
    """A member should not be able to delete their registration when the events sign off deadline has passed."""
    event = EventFactory(sign_off_deadline=today() - timedelta(days=1))
    registration = RegistrationFactory(user=member, event=event)
    client = get_api_client(user=member)

    url = _get_registration_detail_url(registration)
    response = client.delete(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name", [AdminGroup.PROMO, AdminGroup.NOK,],
)
def test_delete_another_registration_as_member_in_nok_or_promo(
    member, group_name, user
):
    """A member of NOK or PROMO should not be able to delete another registration for an event."""
    registration = RegistrationFactory(user=user)
    client = get_api_client(user=member, group_name=group_name)
    response = client.delete(_get_registration_detail_url(registration))

    assert response.status_code == status.HTTP_403_FORBIDDEN


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
    event = EventFactory(sign_off_deadline=today() - timedelta(days=1))
    registration = RegistrationFactory(user=member, event=event)
    client = get_api_client(user=admin_user)

    url = _get_registration_detail_url(registration)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK
