import pytest
from rest_framework import status

from app.common.enums import AdminGroup
from app.util.test_utils import get_api_client

GROUP_URL = "/groups/"


def _get_group_url(group=None):
    return f"{GROUP_URL}{group.slug}/" if (group) else f"{GROUP_URL}"


def _get_group_post_data(group):
    return {
        "name": group.name,
        "slug": group.slug,
    }


def _get_group_put_data(group):
    return {**_get_group_post_data(group), "description": "New Description"}


def get_group_post_data(type):
    return {
        "name": "navn",
        "slug": "slug",
        "type": type
    }


@pytest.mark.django_db
def test_list_as_anonymous_user(default_client):
    """Tests if an anonymous user can list groups"""

    url = _get_group_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_as_anonymous_user(default_client, group):
    """Tests if an anonymous user can retrieve a group"""

    url = _get_group_url(group)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_as_user(group, user):
    """Tests if a logged in user can retrieve a group"""

    client = get_api_client(user=user)
    url = _get_group_url(group)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_as_anonymous_user(default_client, group):
    """Tests if an anonymous user fails to update a group"""

    url = _get_group_url(group)
    response = default_client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_user(group, user):
    """Tests if a logged in user fails to update a group"""

    client = get_api_client(user=user)
    url = _get_group_url(group)
    response = client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code", "new_description"),
    [
        (AdminGroup.HS, status.HTTP_200_OK, "New Description"),
        (AdminGroup.INDEX, status.HTTP_200_OK, "New Description"),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN, None),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN, None),
        ("Non_admin_group", status.HTTP_403_FORBIDDEN, None),
    ],
)
def test_update_as_group_user(
        group,
        user,
        group_name,
        expected_status_code,
        new_description,
):
    """Tests if diffierent groups ability to update a group"""
    expected_description = new_description if new_description else group.description

    client = get_api_client(user=user, group_name=group_name)
    url = _get_group_url(group)
    data = _get_group_put_data(group=group)
    response = client.put(url, data=data)
    group.refresh_from_db()

    assert response.status_code == expected_status_code
    assert group.description == expected_description


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_type",
    ("BOARD", "SUBGROUP", "COMMITTEE", "INTERESTGROUP")
)
def test_create_new_group_as_member(member, group_type):
    """Member should not be able to create a new group"""
    client = get_api_client(user=member)
    url = GROUP_URL
    data = get_group_post_data(group_type)

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_type",
    ("BOARD", "SUBGROUP", "COMMITTEE", "INTERESTGROUP")
)
def test_create_new_group_as_hs(group_type, admin_user):
    """HS members should be allowed to create a new group"""
    client = get_api_client(user=admin_user)
    url = GROUP_URL
    data = get_group_post_data(group_type)

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_type",
    ("BOARD", "SUBGROUP", "COMMITTEE", "INTERESTGROUP")
)
def test_create_new_group_as_index(group_type, index_member):
    """Index members should be allowed to create a new group"""
    client = get_api_client(user=index_member)
    url = GROUP_URL
    data = get_group_post_data(group_type)

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_type",
    ("TIHLDE", "STUDYYEAR", "STUDY", "OTHER")
)
def test_create_new_group_with_invalid_group_type_as_index(group_type, index_member):
    """Index members with invalid group type should not be allowed to create a new group"""
    client = get_api_client(user=index_member)
    url = GROUP_URL
    data = get_group_post_data(group_type)

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
