from rest_framework import status

import pytest

from app.common.enums import AdminGroup, UserClass, UserStudy
from app.util.test_utils import get_api_client

API_CHEATSHEET_BASE_URL = "/api/v1/cheatsheet/"


def get_study(study):
    return UserStudy(study).name


def get_grade(grade):
    return UserClass(grade).value


def _get_cheatsheet_url(cheatsheet):
    return f"{API_CHEATSHEET_BASE_URL}{get_study(cheatsheet.study)}/{get_grade(cheatsheet.grade)}/files/"


def _get_cheatsheet_url_one(cheatsheet):
    return f"{API_CHEATSHEET_BASE_URL}{get_study(cheatsheet.study)}/{get_grade(cheatsheet.grade)}/files/{cheatsheet.id}/"


def _get_cheatsheet_data(cheatsheet):
    return {
        "title": cheatsheet.title,
        "creator": cheatsheet.creator,
        "course": cheatsheet.course,
        "url": cheatsheet.url,
    }


@pytest.mark.django_db
def test_list_as_anonymous_user(default_client, cheatsheet):
    """An anonymous user should not be able to list all cheatsheets"""
    url = _get_cheatsheet_url(cheatsheet)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_as_member(cheatsheet, member):
    """
    A member of TIHLDE should be able to list all cheatsheets.
    """
    client = get_api_client(user=member)
    url = _get_cheatsheet_url(cheatsheet)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json())


@pytest.mark.django_db
def test_update_as_anonymous_user(cheatsheet, default_client):
    """An anonymous user should not be able to update a cheatsheet entity."""

    data = _get_cheatsheet_data(cheatsheet)

    url = _get_cheatsheet_url(cheatsheet)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_admin_member(cheatsheet, user):
    """An admin user should be able to update a cheatsheet entity."""

    data = _get_cheatsheet_data(cheatsheet)
    client = get_api_client(user=user, group_name=AdminGroup.HS)
    url = _get_cheatsheet_url_one(cheatsheet)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_as_admin_member(cheatsheet, admin_user):
    """An admin user should be able to create a cheatsheet entity."""

    data = _get_cheatsheet_data(cheatsheet)
    client = get_api_client(user=admin_user)
    url = _get_cheatsheet_url(cheatsheet)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_as_anonymous_user(cheatsheet, default_client):
    """An anonymous user should not be able to create a cheatsheet entity."""

    data = _get_cheatsheet_data(cheatsheet)

    url = _get_cheatsheet_url_one(cheatsheet)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_as_user(user, cheatsheet):
    """A user should not be able to to delete an cheatsheet entity."""

    client = get_api_client(user=user)
    url = _get_cheatsheet_url_one(cheatsheet)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_as_admin_user(user, cheatsheet, admin_user):
    """A user should be able to to delete an cheatsheet entity."""

    client = get_api_client(user=admin_user)
    url = _get_cheatsheet_url_one(cheatsheet)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK
