from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.common.enums import NativeMembershipType as MembershipType
from app.group.factories.membership_factory import MembershipHistoryFactory
from app.util.test_utils import get_api_client

GROUP_URL = "/groups"


def _get_membership_history_url(membership_history=None, group=None):
    return f"{GROUP_URL}/{group.slug if group else membership_history.group.slug}/membership-histories/"


def _get_membership_history_url_detail(membership_history):
    return f"{_get_membership_history_url(membership_history)}{membership_history.id}/"


def _get_post_membership_history_data(user=None, leader=False):
    return {
        "user": user.user_id,
        "membership_type": "LEADER" if (leader) else "MEMBER",
        "start_date": "2018-01-22T15:00:00.000000+02:00",
        "end_date": "2020-05-03T15:00:00.000000+02:00",
    }


def _get_put_membership_history_data(leader=False):
    return {
        "membership_type": "LEADER" if (leader) else "MEMBER",
        "start_date": "2018-01-22T15:00:00.000000+02:00",
        "end_date": "2020-05-03T15:00:00.000000+02:00",
    }


@pytest.mark.django_db
def test_list_as_anonymous_user(default_client, membership_history):
    """Tests if an anonymous user can list membership histories for a group"""

    url = _get_membership_history_url(membership_history)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_as_anonymous_user(default_client, membership_history):
    """Tests if an anonymous user can retrieve a membership history"""
    url = _get_membership_history_url_detail(membership_history)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_as_user(membership_history, member):
    """Tests if a logged in user can retrieve a membership history"""

    client = get_api_client(user=member)
    url = _get_membership_history_url_detail(membership_history)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_as_anonymous_user(default_client, membership_history):
    """Tests if an anonymous user fails to update a membership history"""

    url = _get_membership_history_url_detail(membership_history)
    response = default_client.put(url, _get_put_membership_history_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_user(user, membership_history):
    """Tests if a logged in user can fails to update a membership history"""

    client = get_api_client(user=user)
    url = _get_membership_history_url_detail(membership_history)
    response = client.put(url, _get_put_membership_history_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        ("Non_admin_group", status.HTTP_403_FORBIDDEN),
    ],
)
def test_update_as_group_user(
    membership_history, user, group_name, expected_status_code
):
    """Tests if different groups ability to update a membership history"""
    client = get_api_client(user=user, group_name=group_name)
    url = _get_membership_history_url_detail(membership_history)
    response = client.put(url, _get_put_membership_history_data())
    membership_history.refresh_from_db()

    assert response.status_code == expected_status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_201_CREATED),
        (AdminGroup.INDEX, status.HTTP_201_CREATED),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        ("Non_admin_group", status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_as_group_user(user, group_name, expected_status_code, group):
    """Tests if different groups ability to create a membership history"""

    client = get_api_client(user=user, group_name=group_name)
    url = _get_membership_history_url(group=group)
    data = _get_post_membership_history_data(user=user)
    response = client.post(url, data=data, format="json")

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_delete_membership_history_as_group_leader(membership_leader):
    """Tests that a group leader can update a membership history"""
    membership = MembershipHistoryFactory(
        group=membership_leader.group, membership_type=MembershipType.MEMBER
    )
    client = get_api_client(user=membership_leader.user)
    url = _get_membership_history_url_detail(membership)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_membership_history_as_group_leader(membership_leader):
    """Tests that a group leader can update a membership history"""
    membership = MembershipHistoryFactory(
        group=membership_leader.group, membership_type=MembershipType.MEMBER
    )
    client = get_api_client(user=membership_leader.user)
    url = _get_membership_history_url_detail(membership)
    response = client.put(url, _get_put_membership_history_data())

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_membership_history_as_group_leader(membership_leader, user):
    """Tests that a group leader can create a member membership history"""

    client = get_api_client(user=membership_leader.user)
    url = _get_membership_history_url(group=membership_leader.group)
    data = _get_post_membership_history_data(user=user)
    response = client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
