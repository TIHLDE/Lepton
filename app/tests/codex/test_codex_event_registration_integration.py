from rest_framework import status

import pytest

from app.codex.enums import CodexGroups
from app.common.enums import NativeMembershipType as MembershipType
from app.util.test_utils import add_user_to_group_with_name, get_api_client

CODEX_EVENT_BASE_URL = "/codex/events/"


def get_registration_url(event_id):
    return f"{CODEX_EVENT_BASE_URL}{event_id}/registrations/"


def get_registration_detail_url(event_id, registration_id):
    return f"{CODEX_EVENT_BASE_URL}{event_id}/registrations/{registration_id}/"


def get_registration_data(event):
    return {
        "event": event.id,
    }


@pytest.mark.django_db
def test_create_codex_event_registration_as_anonymous_user(codex_event):
    """An anonymous user should not be able to create a registration for a event."""
    client = get_api_client()

    url = get_registration_url(codex_event.id)
    data = get_registration_data(codex_event)

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_codex_event_registration_as_authenticated_user(member, codex_event):
    """An authenticated user should not be able to create a registration for a event."""
    client = get_api_client(member)

    url = get_registration_url(codex_event.id)
    data = get_registration_data(codex_event)

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_create_codex_event_registration_as_codex_member(
    member, codex_group, codex_event
):
    """A codex member should be able to create a registration for a event."""
    add_user_to_group_with_name(member, codex_group)

    client = get_api_client(member)
    url = get_registration_url(codex_event.id)
    data = get_registration_data(codex_event)

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["user_info"]["user_id"] == member.user_id
    assert response.data["order"] == 0


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_create_codex_event_registration_as_codex_member_with_correct_order(
    member, codex_group, codex_event, codex_event_registration
):
    """A codex member should be able to create a registration and the order should be correct."""
    add_user_to_group_with_name(member, codex_group)

    codex_event_registration.event = codex_event
    codex_event_registration.save()

    client = get_api_client(member)
    url = get_registration_url(codex_event.id)
    data = get_registration_data(codex_event)

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["user_info"]["user_id"] == member.user_id
    assert response.data["order"] == codex_event_registration.order + 1


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_delete_own_codex_event_registration_as_codex_member(
    member, codex_group, codex_event_registration
):
    """A codex member should be able to delete their own registration."""
    add_user_to_group_with_name(member, codex_group)

    codex_event_registration.user = member
    codex_event_registration.save()

    client = get_api_client(member)
    url = get_registration_detail_url(
        codex_event_registration.event.id, codex_event_registration.registration_id
    )

    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_delete_other_codex_event_registration_as_codex_member(
    member, codex_group, codex_event_registration
):
    """A codex member should not be able to delete another user's registration."""
    add_user_to_group_with_name(member, codex_group)

    client = get_api_client(member)
    url = get_registration_detail_url(
        codex_event_registration.event.id, codex_event_registration.registration_id
    )

    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_delete_other_codex_event_registration_as_codex_group_leader(
    member, codex_group, codex_event_registration
):
    """A codex group leader should be able to delete another user's registration."""
    add_user_to_group_with_name(
        member, codex_group, membership_type=MembershipType.LEADER
    )

    client = get_api_client(member)
    url = get_registration_detail_url(
        codex_event_registration.event.id, codex_event_registration.registration_id
    )

    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK
