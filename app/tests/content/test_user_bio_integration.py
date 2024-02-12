from rest_framework import status

import pytest

from app.content.factories.user_bio_factory import UserBioFactory


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
@pytest.mark.parametrize(
    ("user_bio"),
     [
         UserBioFactory,
     ],
)
def test_update_bio_as_anonymous_user(default_client, user_bio):
    """An anonymous user should not be able to update a user's bio"""
    user_bio = user_bio()
    url = _get_bio_url(user_bio)
    data = _get_user_bio_put_data()

    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    user_bio.refresh_from_db()
    assert user_bio.description != data["description"]
