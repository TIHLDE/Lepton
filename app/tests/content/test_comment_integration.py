import pytest

from app.util.test_utils import get_api_client
from rest_framework import status

API_COMMENTS_BASE_URL = "/comments/"

def get_comment_data(content_id):
    return {
        "body": "Hei lol",
        "parent": None,
        "content_type": "event",
        "content_id": content_id
    }

@pytest.mark.django_db
def test_create_comment_as_member(member, event):
    data = get_comment_data(event.id)
    client = get_api_client(user=member)

    response = client.post(API_COMMENTS_BASE_URL, data=data)

    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_comment_as_admin(admin_user, event):
    data = get_comment_data(event.id)
    client = get_api_client(user=admin_user)

    response = client.post(API_COMMENTS_BASE_URL, data=data)

    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_comment_as_anonymous_user(default_client, event):
    data = get_comment_data(event.id)

    response = default_client.post(API_COMMENTS_BASE_URL, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN