from rest_framework import status

import pytest

from app.util.test_utils import get_api_client

SHORT_LINK_URL = "/short-links/"


def _get_short_link_url(short_link=None):
    return (
        f"{SHORT_LINK_URL}{short_link.name}/" if (short_link) else f"{SHORT_LINK_URL}"
    )


@pytest.fixture()
def short_link_post_data(short_link):
    return {
        "name": "new_short_link",
        "url": short_link.url,
    }


@pytest.mark.django_db
def test_list_as_anonymous_user_fails(default_client):
    """Tests if an anonymous user can list short links"""

    url = _get_short_link_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_list_as_user(member):
    """Tests if an logged in user can list short links"""

    client = get_api_client(user=member)
    url = _get_short_link_url()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_as_anonymous_user(default_client, short_link):
    """Tests if an anonymous user can retrieve a short link"""

    url = _get_short_link_url(short_link)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_as_user(short_link, member):
    """Tests if a logged in user can retrieve a short link"""

    client = get_api_client(user=member)
    url = _get_short_link_url(short_link)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_as_anonymous(default_client, short_link_post_data):
    """An anonymous user should not be able to create a short link."""
    response = default_client.post(_get_short_link_url(), short_link_post_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_as_user(member, short_link_post_data):
    """A logged in user should be able to create a short link."""
    client = get_api_client(user=member)
    response = client.post(_get_short_link_url(), short_link_post_data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("link_name", "status_code"),
    [
        ("om/noe", status.HTTP_409_CONFLICT),
        ("om/", status.HTTP_409_CONFLICT),
        ("om", status.HTTP_409_CONFLICT),
        ("a/12", status.HTTP_409_CONFLICT),
        ("a/", status.HTTP_409_CONFLICT),
        ("a", status.HTTP_409_CONFLICT),
        ("k/12", status.HTTP_409_CONFLICT),
        ("k/", status.HTTP_409_CONFLICT),
        ("k", status.HTTP_409_CONFLICT),
        ("n/12", status.HTTP_409_CONFLICT),
        ("n/", status.HTTP_409_CONFLICT),
        ("n", status.HTTP_409_CONFLICT),
        ("ba/12", status.HTTP_200_OK),
        ("ba/", status.HTTP_200_OK),
        ("ba", status.HTTP_200_OK),
    ],
)
def test_create_reserved_as_user(member, short_link_post_data, link_name, status_code):
    """
    A logged in user should not be able to create a short link
    which starts with a reserved keyword.
    """
    client = get_api_client(user=member)
    data = short_link_post_data
    data["name"] = link_name
    response = client.post(_get_short_link_url(), data)

    assert response.status_code == status_code


@pytest.mark.django_db
def test_create_duplicate_name_as_user(member, short_link_post_data, short_link):
    """
    A logged in user should not be able to create a short link
    which has a name equal to existing name.
    """
    client = get_api_client(user=member)
    data = short_link_post_data
    data["name"] = short_link.name
    response = client.post(_get_short_link_url(), data)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.django_db
def test_destroy_as_anonymous(default_client, short_link):
    """An anonymous user should not be able to delete a short link"""
    url = _get_short_link_url(short_link)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_destroy_as_user(user, short_link):
    """An logged in user should not be able to delete a short link"""
    client = get_api_client(user=user)
    url = _get_short_link_url(short_link)
    response = client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_destroy_as_owner(short_link):
    """The owner should be able to delete a short link"""
    client = get_api_client(user=short_link.user)
    url = _get_short_link_url(short_link)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK
