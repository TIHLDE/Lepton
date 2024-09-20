from rest_framework import status

import pytest

from app.common.enums import (
    AdminGroup,
    Groups
)
from app.content.factories import ToddelFactory
from app.util.test_utils import get_api_client

API_TODDEL_BASE_URL = "/toddel/"


def _get_toddel_detail_url(toddel):
    return f"{API_TODDEL_BASE_URL}{toddel.edition}/"


def _get_toddel_post_data():
    return {
        "edition": 1,
        "title": "Töddel title",
        "image": "https://macbasics.files.wordpress.com/2013/06/umlaut21.jpg",
        "pdf": "https://www.imore.com/sites/imore.com/files/styles/large/public/images/stories/2010/04/time-100401.png",
        "published_at": "2022-02-22",
    }


def _get_toddel_put_data(toddel):
    return {
        "edition": toddel.edition,
        "title": toddel.title,
        "image": toddel.image,
        "pdf": toddel.pdf,
        "published_at": toddel.published_at,
    }


@pytest.mark.django_db
def test_toddel_ordering(default_client):
    """Toddel should be ordered by edition descending (newest first)."""
    first_edition = ToddelFactory(edition=1)
    second_edition = ToddelFactory(edition=2)

    response = default_client.get(API_TODDEL_BASE_URL)
    response = response.json()

    assert response["results"][0].get("title") == second_edition.title
    assert response["results"][1].get("title") == first_edition.title


@pytest.mark.django_db
def test_list_as_anonymous(default_client):
    """An anonymous user should be able to retrieve Toddels."""
    response = default_client.get(API_TODDEL_BASE_URL)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_as_member(member):
    """A member should be able to retrieve Toddels."""
    client = get_api_client(user=member)

    response = client.get(API_TODDEL_BASE_URL)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_as_anonymous(default_client, toddel):
    """An anonymous user should not be able to update a Toddel."""
    data = _get_toddel_put_data(toddel)
    url = _get_toddel_detail_url(toddel)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_member(member, toddel):
    """A member should not be able to update a Toddel."""
    client = get_api_client(user=member)
    data = _get_toddel_put_data(toddel)
    url = _get_toddel_detail_url(toddel)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (Groups.REDAKSJONEN, status.HTTP_200_OK),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
    ],
)
def test_update_as_member_of_group(member, toddel, group_name, expected_status_code):
    """Only members of HS, Index or Redaksjonen should be able to update a Toddel."""
    client = get_api_client(user=member, group_name=group_name)
    data = _get_toddel_put_data(toddel)
    url = _get_toddel_detail_url(toddel)
    response = client.put(url, data)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_create_as_anonymous(default_client):
    """An anonymous user should not be able to create a Toddel."""
    response = default_client.post(API_TODDEL_BASE_URL, _get_toddel_post_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_as_member(member):
    """A member should not be able to create a Toddel."""
    client = get_api_client(user=member)
    response = client.post(API_TODDEL_BASE_URL, _get_toddel_post_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_201_CREATED),
        (AdminGroup.INDEX, status.HTTP_201_CREATED),
        (Groups.REDAKSJONEN, status.HTTP_201_CREATED),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_as_member_of_admin_group(member, group_name, expected_status_code):
    """Only members of HS, Index or Redaksjonen should be able to create a Toddel."""
    client = get_api_client(user=member, group_name=group_name)
    response = client.post(API_TODDEL_BASE_URL, _get_toddel_post_data())

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_destroy_as_anonymous(default_client, toddel):
    """An anonymous user should not be able to delete a Toddel."""
    url = _get_toddel_detail_url(toddel)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_destroy_as_member(member, toddel):
    """A member should not be able to delete a Toddel."""
    client = get_api_client(user=member)
    url = _get_toddel_detail_url(toddel)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (Groups.REDAKSJONEN, status.HTTP_200_OK),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
    ],
)
def test_destroy_as_member_of_admin_group(
    toddel, member, group_name, expected_status_code
):
    """Only members of HS, Index or Redaksjonen should be able to delete a Toddel."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_toddel_detail_url(toddel)
    response = client.delete(url)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_destroy_returns_detail_in_response(toddel, member):
    """Should return a detail message in the response."""
    client = get_api_client(user=member, group_name=AdminGroup.INDEX)
    url = _get_toddel_detail_url(toddel)
    response = client.delete(url)

    assert response.json().get("detail")
