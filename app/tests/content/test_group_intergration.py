from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.util.test_utils import get_api_client

GROUP_URL = "/api/v1/group/"


def _get_group_url(group=None):
    return f"{GROUP_URL}{group.slug}/" if (group) else f"{GROUP_URL}"


def _get_group_post_data(group):
    return {
        "name": group.name,
        "slug": group.slug,
    }


def _get_group_put_data(group):
    return {**_get_group_post_data(group), "description": "New Description"}


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
    """Tests if an anonymous user can fails to update a group"""

    url = _get_group_url(group)
    response = default_client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_user(group, user):
    """Tests if a logged in user can fails to update a group"""

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
        (AdminGroup.NOK, status.HTTP_200_OK, "New Description"),
        (AdminGroup.PROMO, status.HTTP_200_OK, "New Description"),
        ("Non_admin_group", status.HTTP_403_FORBIDDEN, None),
    ],
)
def test_update_as_group_user(
    group, user, group_name, expected_status_code, new_description,
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
def test_create_makes_group_if_not_found(group, user):
    """Tests if that a group is created if it doesn't exits"""

    name = group.name

    client = get_api_client(user=user, group_name=AdminGroup.HS)
    url = _get_group_url()
    data = _get_group_post_data(group=group)
    response = client.post(url, data=data)
    group.refresh_from_db()

    assert group.name == name
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_return_group_if_found(group, user):

    """Tests if that a group is returned if it does exits when trying to create  a group"""

    name = group.name

    client = get_api_client(user=user, group_name=AdminGroup.HS)
    url = _get_group_url()
    data = _get_group_post_data(group=group)
    response = client.post(url, data=data)
    response = client.post(url, data=data)
    group.refresh_from_db()

    assert group.name == name
    assert response.status_code == status.HTTP_200_OK
