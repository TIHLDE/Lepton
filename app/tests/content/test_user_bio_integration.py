from rest_framework import status

import pytest

pytestmark = pytest.mark.django_db

API_USER_BIO_BASE_URL = "/user-bios/"

def _get_user_bio_data():
    return {
        "description": "this is my description",
        "gitHub_link": "https://www.github.com",
        "linkedIn_link": "https://www.linkedIn.com"
    }

@pytest.mark.django_db
def test_create_user_bio(member, api_client):
    """A user should be able to create a user bio"""
    data = _get_user_bio_data()
    client = api_client(user=member)
    response = client.post(API_USER_BIO_BASE_URL, data)

    assert response.status_code == status.HTTP_201_CREATED
