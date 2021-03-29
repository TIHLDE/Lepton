from rest_framework import status

import pytest

from app.common.enums import AdminGroup, MembershipType
from app.group.factories.membership_factory import MembershipFactory
from app.util.test_utils import get_api_client

GROUP_URL = "/api/v1/group"


def _get_membership_url(membership=None, group = None):
    return f"{GROUP_URL}/{group.slug if group else membership.group.slug}/membership/"


def _get_membership_url_detail(membership):
    return f"{_get_membership_url(membership)}{membership.user.user_id}/"


def _get_membership_data(membership=None, leader=False):
    return {
        "user": {"user_id": membership.user.user_id},
        "group": {"group": membership.group.slug},
        "membership_type": "LEADER" if (leader) else "MEMBER",
    }


def _get_post_membership_data(group=None, user=None, leader=False):
    return {
        "user": {"user_id": user.user_id},
        "group": {"group": group.slug},
        "membership_type": "LEADER" if (leader) else "MEMBER",
    }


@pytest.mark.django_db
def test_list_as_anonymous_user(default_client, membership):
    """Tests if an anonymous user can list memberships for a group"""

    url = _get_membership_url(membership)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_as_anonymous_user(default_client, membership):
    """Tests if an anonymous user can retrieve a membership"""
    url = _get_membership_url_detail(membership)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_as_user(membership, user):
    """Tests if a logged in user can retrieve a membership"""

    client = get_api_client(user=user)
    url = _get_membership_url_detail(membership)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_as_anonymous_user(default_client, membership):
    """Tests if an anonymous user can fails to update a membership"""

    url = _get_membership_url_detail(membership)
    response = default_client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_user(user, membership):
    """Tests if a logged in user can fails to update a membership"""

    client = get_api_client(user=user)
    url = _get_membership_url_detail(membership)
    response = client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code", "membership_type"),
    [
        (AdminGroup.HS, status.HTTP_200_OK, MembershipType.LEADER),
        (AdminGroup.INDEX, status.HTTP_200_OK, MembershipType.LEADER),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN, MembershipType.MEMBER),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN, MembershipType.MEMBER),
        ("Non_admin_group", status.HTTP_403_FORBIDDEN, None),
    ],
)
def test_update_as_group_user(
    membership, user, group_name, expected_status_code, membership_type, group
):
    """Tests if different groups ability to update a membership """
    expected_membership_type = (
        membership_type if membership_type else membership.membership_type
    )

    client = get_api_client(user=user, group_name=group_name)
    url = _get_membership_url_detail(membership)
    data = _get_membership_data(membership=membership, leader=True)
    response = client.put(url, data=data, format="json")
    membership.refresh_from_db()

    assert response.status_code == expected_status_code
    assert membership.membership_type == expected_membership_type

@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK ),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        ("Non_admin_group", status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_as_group_user(
    user, group_name, expected_status_code, group
):
    """Tests if different groups ability to create a membership """

    client = get_api_client(user=user, group_name=group_name)
    url = _get_membership_url(group=group)
    data = _get_post_membership_data(group=group, user=user)
    response = client.post(url, data=data, format="json")

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_create_member_membership(admin_user, group, membership_leader):
    """Test if you can create a membership that has the membership type member """

    client = get_api_client(user=admin_user)
    url = _get_membership_url(membership_leader)
    data = _get_post_membership_data(group, admin_user, leader=False)
    response = client.post(url, data=data, format="json")

    assert response.json()["membership_type"] == str(MembershipType.MEMBER).upper()
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_leader_membership(admin_user, group, membership_leader):
    """Test if you can't create a membership that has the membership type leader"""
    client = get_api_client(user=admin_user)
    url = _get_membership_url(membership_leader)
    data = _get_post_membership_data(group, admin_user, leader=True)
    response = client.post(url, data=data, format="json")

    assert response.json()["membership_type"] == str(MembershipType.MEMBER).upper()
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_membership_as_group_leader(user, group):
    """Tests that a group leader can update a membership"""
    MembershipFactory(user=user, group=group, membership_type=MembershipType.LEADER)
    membership = MembershipFactory(group=group, membership_type=MembershipType.MEMBER)
    client = get_api_client(user=user)
    url = _get_membership_url_detail(membership)
    response = client.put(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_member_membership_as_group_leader(membership_leader, user):
    """Tests that a group leader can create a member membership"""

    client = get_api_client(user=membership_leader.user)
    url = _get_membership_url(membership_leader)
    data = _get_post_membership_data(group=membership_leader.group, user=user)
    response = client.post(url, data=data, format="json")

    assert response.json()["membership_type"] == str(MembershipType.MEMBER).upper()
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_member_membership_to_leader_as_group_leader(
    user, group, membership_leader, membership
):
    """Tests that a group leader can update a member membership to a leader which switches the leader of the group"""

    membership.group = group
    membership_leader.group = group
    membership_leader.user = user
    membership_leader.save()
    membership.save()
    client = get_api_client(user=user)
    url = _get_membership_url_detail(membership)
    data = _get_membership_data(membership, leader=True)
    response = client.put(url, data=data, format="json")
    membership_leader.refresh_from_db()
    membership.refresh_from_db()
    assert membership.membership_type == MembershipType.LEADER
    assert membership_leader.membership_type == MembershipType.MEMBER
    assert response.status_code == status.HTTP_200_OK
