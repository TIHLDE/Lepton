from rest_framework import status

import pytest

from app.blitzed.factories.session_factory import SessionFactory
from app.blitzed.factories.user_wasted_level_factory import (
    UserWastedLevelFactory,
)
from app.blitzed.models.session import Session
from app.common.enums import Groups
from app.content.factories import UserFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client

API_SESSION_BASE_URL = "/blitzed/session/"
API_USER_WASTED_LEVEL_BASE_URL = "/blitzed/user_wasted_level/"


def _get_session_url(session_id=None):
    if session_id is not None:
        return f"{API_SESSION_BASE_URL}{session_id}/"
    return API_SESSION_BASE_URL


def _get_wasted_level_url(wasted_level_id=None):
    if wasted_level_id is not None:
        return f"{API_USER_WASTED_LEVEL_BASE_URL}{wasted_level_id}/"
    return API_USER_WASTED_LEVEL_BASE_URL


@pytest.mark.django_db
def test_that_a_member_can_create_a_session(member):
    """A member should be able to create a drinking session"""
    url = _get_session_url()
    client = get_api_client(user=member)

    data = {
        "start_time": "2023-10-30T12:00:00Z",
        "end_time": "2023-10-30T18:00:00Z",
    }
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_session_specified_creator(member):
    """A member should be able to create a session with a specified creator"""
    url = _get_session_url()
    client = get_api_client(user=member)

    data = {
        "creator": member.user_id,
        "start_time": "2023-10-30T12:00:00Z",
        "end_time": "2023-10-30T18:00:00Z",
    }
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED

    assert Session.objects.count() == 1


@pytest.mark.django_db
def test_create_session_as_user():
    """A user should not be able to create a session"""
    user = UserFactory()

    url = _get_session_url()
    client = get_api_client(user=user)

    data = {
        "start_time": "2023-10-30T12:00:00Z",
        "end_time": "2023-10-30T18:00:00Z",
    }
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_wasted_level():
    sample_session = SessionFactory()

    user1 = UserFactory()
    add_user_to_group_with_name(user1, Groups.TIHLDE)
    user2 = UserFactory()

    UserWastedLevelFactory(user=user1, session=sample_session, blood_alcohol_level=0.08)
    UserWastedLevelFactory(user=user2, session=sample_session, blood_alcohol_level=0.1)

    url = _get_wasted_level_url()
    client = get_api_client(user1)

    wasted_graph_data = {
        "user": user1.user_id,
        "session": sample_session.id,
        "blood_alcohol_level": 0.08,
    }

    response = client.post(url, wasted_graph_data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_wasted_level_as_user():
    """ "A non Tihlde user should not be able to create a wasted level"""
    sample_session = SessionFactory()
    user = UserFactory()

    url = _get_wasted_level_url()
    client = get_api_client(user=user)

    wasted_graph_data = {
        "user": user.user_id,
        "session": sample_session.id,
        "blood_alcohol_level": 0.08,
    }

    response = client.post(url, wasted_graph_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_wasted_level_with_invalid_user():
    """A member should not be able to create a wasted level with an invalid user"""
    sample_session = SessionFactory()
    user = UserFactory()
    add_user_to_group_with_name(user, Groups.TIHLDE)

    url = _get_wasted_level_url()
    client = get_api_client(user=user)

    wasted_graph_data = {
        "user": 999,
        "session": sample_session.id,
        "blood_alcohol_level": 0.08,
    }

    response = client.post(url, wasted_graph_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_wasted_level_with_invalid_session():
    """A member should not be able to create a wasted level with an invalid session"""
    user = UserFactory()
    add_user_to_group_with_name(user, Groups.TIHLDE)

    url = _get_wasted_level_url()
    client = get_api_client(user=user)

    wasted_graph_data = {
        "user": user.user_id,
        "session": 999,
        "blood_alcohol_level": 0.08,
    }

    response = client.post(url, wasted_graph_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_wasted_level_with_invalid_blood_alcohol_level():
    """A member should not be able to create a wasted level with an invalid blood alcohol level"""
    sample_session = SessionFactory()
    user = UserFactory()
    add_user_to_group_with_name(user, Groups.TIHLDE)

    url = _get_wasted_level_url()
    client = get_api_client(user=user)

    wasted_graph_data = {
        "user": user.user_id,
        "session": sample_session.id,
        "blood_alcohol_level": "abc",
    }

    response = client.post(url, wasted_graph_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_add_wasted_level_to_session():
    sample_session = SessionFactory()
    user1 = UserFactory()
    add_user_to_group_with_name(user1, Groups.TIHLDE)
    url = _get_wasted_level_url()
    client = get_api_client(user1)

    initial_level_data = {
        "user": user1.user_id,
        "session": sample_session.id,
        "blood_alcohol_level": 0.08,
    }

    initial_response = client.post(url, initial_level_data)
    assert initial_response.status_code == status.HTTP_201_CREATED

    additional_level_data = {
        "user": user1.user_id,
        "session": sample_session.id,
        "blood_alcohol_level": 0.10,
    }

    additional_response = client.post(url, additional_level_data)
    assert additional_response.status_code == status.HTTP_201_CREATED

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    data = response.data
    assert len(data) == 2

    assert data[0]["blood_alcohol_level"] == "0.10"
    assert data[1]["blood_alcohol_level"] == "0.08"


@pytest.mark.django_db
def test_create_session_user_and_wasted_level():
    session = SessionFactory()
    user = UserFactory()
    add_user_to_group_with_name(user, Groups.TIHLDE)

    client = get_api_client(user)

    session_url = _get_session_url(session.id)
    session_data = {
        "users": [user.user_id],
        "start_time": "2023-10-30T12:00:00Z",
        "end_time": "2023-10-30T18:00:00Z",
    }
    session_response = client.put(session_url, session_data)

    assert session_response.status_code == status.HTTP_200_OK

    assert session.users.count() == 1

    wasted_level_url = _get_wasted_level_url()
    wasted_level_data = {
        "user": user.user_id,
        "session": session.id,
        "blood_alcohol_level": 0.08,
    }
    wasted_level_response = client.post(wasted_level_url, wasted_level_data)

    assert wasted_level_response.status_code == status.HTTP_201_CREATED

    assert user.userwastedlevel_set.count() == 1


@pytest.mark.django_db
def test_create_session_users_and_wasted_levels():
    session = SessionFactory()

    user = UserFactory()
    user2 = UserFactory()
    add_user_to_group_with_name(user, Groups.TIHLDE)
    add_user_to_group_with_name(user2, Groups.TIHLDE)

    client = get_api_client(user)

    session_url = _get_session_url(session.id)
    session_data = {
        "users": [user.user_id, user2.user_id],
        "start_time": "2023-10-30T12:00:00Z",
        "end_time": "2023-10-30T18:00:00Z",
    }
    session_response = client.put(session_url, session_data)

    assert session_response.status_code == status.HTTP_200_OK

    assert session.users.count() == 2

    wasted_level_url = _get_wasted_level_url()
    wasted_level_data = {
        "user": user.user_id,
        "session": session.id,
        "blood_alcohol_level": 0.08,
    }
    wasted_level_response = client.post(wasted_level_url, wasted_level_data)

    assert wasted_level_response.status_code == status.HTTP_201_CREATED

    wasted_level_data_2 = {
        "user": user2.user_id,
        "session": session.id,
        "blood_alcohol_level": 0.10,
    }

    wasted_level_response_2 = client.post(wasted_level_url, wasted_level_data_2)

    assert wasted_level_response_2.status_code == status.HTTP_201_CREATED

    assert user.userwastedlevel_set.count() == 1

    assert user2.userwastedlevel_set.count() == 1


@pytest.mark.django_db
def test_create_session_users_multiple_wasted_levels():
    session = SessionFactory()

    user = UserFactory()
    user2 = UserFactory()
    add_user_to_group_with_name(user, Groups.TIHLDE)
    add_user_to_group_with_name(user2, Groups.TIHLDE)

    client = get_api_client(user)

    session_url = _get_session_url(session.id)
    session_data = {
        "users": [user.user_id, user2.user_id],
        "start_time": "2023-10-30T12:00:00Z",
        "end_time": "2023-10-30T18:00:00Z",
    }
    session_response = client.put(session_url, session_data)

    assert session_response.status_code == status.HTTP_200_OK

    assert session.users.count() == 2

    wasted_level_url = _get_wasted_level_url()
    wasted_level_data = {
        "user": user.user_id,
        "session": session.id,
        "blood_alcohol_level": 0.08,
    }
    wasted_level_response = client.post(wasted_level_url, wasted_level_data)

    assert wasted_level_response.status_code == status.HTTP_201_CREATED

    wasted_level_url = _get_wasted_level_url()
    wasted_level_data_2 = {
        "user": user.user_id,
        "session": session.id,
        "blood_alcohol_level": 0.18,
    }
    wasted_level_response = client.post(wasted_level_url, wasted_level_data_2)

    assert wasted_level_response.status_code == status.HTTP_201_CREATED

    wasted_level_data_3 = {
        "user": user2.user_id,
        "session": session.id,
        "blood_alcohol_level": 0.10,
    }

    wasted_level_response_2 = client.post(wasted_level_url, wasted_level_data_3)

    assert wasted_level_response_2.status_code == status.HTTP_201_CREATED

    assert user.userwastedlevel_set.count() == 2

    assert user2.userwastedlevel_set.count() == 1


@pytest.mark.django_db
def test_create_session_with_invalid_creator(member):
    """A member should not be able to create a session with an invalid creator"""
    url = _get_session_url()
    client = get_api_client(user=member)

    data = {
        "creator": 999,
        "start_time": "2023-10-30T12:00:00Z",
        "end_time": "2023-10-30T18:00:00Z",
    }

    response = client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_session_with_invalid_users():
    """A member should not be able to create a session with invalid users"""
    user = UserFactory()
    add_user_to_group_with_name(user, Groups.TIHLDE)

    url = _get_session_url()
    client = get_api_client(user)

    data = {
        "creator": user.user_id,
        "users": [999],
        "start_time": "2023-10-30T12:00:00Z",
        "end_time": "2023-10-30T18:00:00Z",
    }

    response = client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
