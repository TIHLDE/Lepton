from rest_framework import status

import pytest

from app.content.factories.user_bio_factory import UserBioFactory
from app.content.models.user_bio import UserBio
from app.tests.conftest import user_bio
from app.util.test_utils import get_api_client

pytestmark = pytest.mark.django_db

API_USER_BIO_BASE_URL = "/user-bios/"


def _get_bio_url(user_bio):
    return f"{API_USER_BIO_BASE_URL}{user_bio.id}/"


def _get_user_bio_post_data():
    return {
        "description": "this is my description",
        "gitHub_link": "https://www.github.com",
        "linkedIn_link": "https://www.linkedIn.com",
    }


def _get_user_bio_put_data():
    return {
        "description": "New description",
    }


@pytest.mark.django_db
def test_create_user_bio(member, api_client):
    """A user should be able to create a user bio"""
    data = _get_user_bio_post_data()
    client = api_client(user=member)
    response = client.post(API_USER_BIO_BASE_URL, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_duplicate_user_bio(member, api_client, user_bio):
    """A user should not be able to create a duplicate user bio"""
    user_bio.user = member
    user_bio.save()

    data = _get_user_bio_post_data()
    client = api_client(user=member)
    response = client.post(API_USER_BIO_BASE_URL, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_bio_as_anonymous_user(default_client, user_bio):
    """An anonymous user should not be able to update a user's bio"""
    url = _get_bio_url(user_bio)
    data = _get_user_bio_put_data()
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    user_bio.refresh_from_db()
    assert user_bio.description != data["description"]


@pytest.mark.django_db
def test_update_own_bio_as_user(member, user_bio):
    """An user should be able to update their own bio"""
    user_bio.user = member
    user_bio.save()
    url = _get_bio_url(user_bio)
    client = get_api_client(user=member)
    data = _get_user_bio_put_data()
    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    user_bio.refresh_from_db()
    assert user_bio.description == data["description"]


@pytest.mark.django_db
def test_update_another_users_bio(member, user_bio):
    """An user should not be able to update another user's bio"""
    url = _get_bio_url(user_bio)
    client = get_api_client(user=member)
    data = _get_user_bio_put_data()
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    user_bio.refresh_from_db()
    assert user_bio.description != data["description"]


@pytest.mark.django_db
def test_destroy_bio_as_anonymous_user(default_client, user_bio):
    """An anonymous user should not be able to destroy a user's bio"""
    url = _get_bio_url(user_bio)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert len(UserBio.objects.filter(id=user_bio.id))


@pytest.mark.django_db
def test_destroy_own_bio(user_bio, member):
    """An user should be able to destroy their own user's bio"""
    user_bio.user = member
    user_bio.save()
    url = _get_bio_url(user_bio)
    client = get_api_client(user=member)
    response = client.delete(url)
    assert response.status_code == status.HTTP_200_OK
    assert not len(UserBio.objects.filter(id=user_bio.id))


@pytest.mark.django_db
def test_destroy_other_bios(member, user_bio):
    """An user should not be able to delete another user's bio"""
    url = _get_bio_url(user_bio)
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert len(UserBio.objects.filter(id=user_bio.id))
