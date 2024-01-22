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

def get_comment_update_data(body):
    return {
        "body": body
    }

@pytest.mark.django_db
def test_create_comment_as_member(member, event):
    """A member should be able to create a comment"""
    data = get_comment_data(event.id)
    client = get_api_client(user=member)

    response = client.post(API_COMMENTS_BASE_URL, data=data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_comment_as_admin(admin_user, event):
    """An admin should be able to create a comment"""
    data = get_comment_data(event.id)
    client = get_api_client(user=admin_user)

    response = client.post(API_COMMENTS_BASE_URL, data=data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_comment_as_anonymous_user(default_client, event):
    """An anonymous usershould not be able to create a comment"""
    data = get_comment_data(event.id)

    response = default_client.post(API_COMMENTS_BASE_URL, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_own_comment_as_member(member, comment):
    """A member should be able to update his own comment"""
    comment.author = member
    comment.save()

    NEW_BODY = "test update"
    data = get_comment_update_data(NEW_BODY)
    client = get_api_client(user=member)

    response = client.put(f"{API_COMMENTS_BASE_URL}{comment.id}/", data=data)

    assert response.status_code == status.HTTP_200_OK
    comment.refresh_from_db()
    assert comment.body == NEW_BODY

@pytest.mark.django_db
def test_update_others_comment_as_member(member, comment):
    """A member should not be able to update another persons comment"""
    data = get_comment_update_data("test update")
    client = get_api_client(user=member)

    response = client.put(f"{API_COMMENTS_BASE_URL}{comment.id}/", data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_destroy_own_comment_as_member(member, comment):
    """A member should be able to delete his own comment"""
    comment.author = member
    comment.save()

    client = get_api_client(user=member)

    response = client.delete(f"{API_COMMENTS_BASE_URL}{comment.id}/")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_destroy_others_comment_as_member(member, comment):
    """A member should not be able to delete another persons comment"""
    client = get_api_client(user=member)

    response = client.delete(f"{API_COMMENTS_BASE_URL}{comment.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_destroy_comment_as_admin(admin_user, comment):
    """An admin should be able to delete a comment"""
    client = get_api_client(user=admin_user)

    response = client.delete(f"{API_COMMENTS_BASE_URL}{comment.id}/")

    assert response.status_code == status.HTTP_200_OK

