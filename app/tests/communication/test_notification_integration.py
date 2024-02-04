from rest_framework import status

import pytest

from app.util.test_utils import get_api_client

NOTIFICATION_URL = "/notifications/"


def _get_notification_url(notification=None):
    return (
        f"{NOTIFICATION_URL}{notification.id}/"
        if notification
        else f"{NOTIFICATION_URL}"
    )


def _get_notification_put_data(notification):
    return {
        "read": not notification.read,
    }


def _get_notification_post_data():
    return {
        "title": "Test notification",
        "description": "Test description",
        "link": "https://tihlde.org",
    }


@pytest.mark.django_db
def test_list_notifications_as_anonymous_user_fails(default_client):
    """Tests if an anonymous user can list notifications"""

    url = _get_notification_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_notifications_as_member_self(member):
    """Tests if a member can list their own notifications"""

    client = get_api_client(user=member)
    url = _get_notification_url()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_notification_as_anonymous_user(default_client, notification):
    """Tests if an anonymous user can retrieve a notification"""

    url = _get_notification_url(notification)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_notification_as_member(notification, member):
    """Tests if a logged in user can retrieve another user's notification"""

    client = get_api_client(user=member)
    url = _get_notification_url(notification)
    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_retrieve_notification_as_owner(notification, member):
    """Tests if a logged in user can retrieve it's own notification"""

    notification.user = member
    notification.save()

    client = get_api_client(user=member)
    url = _get_notification_url(notification)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_notification_as_anonymous(default_client):
    """An anonymous user should not be able to create a notification."""
    response = default_client.post(_get_notification_url())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_notification_as_user(member):
    """A logged in user should not be able to create a notification."""
    client = get_api_client(user=member)
    data = _get_notification_post_data()
    response = client.post(_get_notification_url(), data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_notification_as_anonymous(default_client, notification):
    """An anonymous user should not be able to update a notification"""
    url = _get_notification_url(notification)
    data = _get_notification_put_data(notification=notification)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_notification_as_user(user, notification):
    """An logged in user should not be able to update a notification"""
    client = get_api_client(user=user)
    url = _get_notification_url(notification)
    data = _get_notification_put_data(notification=notification)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_notification_as_owner(notification, member):
    """The owner should be able to update a notification"""

    notification.user = member
    notification.save()

    client = get_api_client(user=member)
    url = _get_notification_url(notification)
    data = _get_notification_put_data(notification=notification)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["read"] == data["read"]


@pytest.mark.django_db
def test_destroy_notification_as_anonymous(default_client, notification):
    """An anonymous user should not be able to delete a notification"""
    url = _get_notification_url(notification)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_destroy_notification_as_user(user, notification):
    """An logged in user should not be able to delete a notification"""
    client = get_api_client(user=user)
    url = _get_notification_url(notification)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_destroy_notification_as_owner(notification):
    """The owner should not be able to delete a notification"""
    client = get_api_client(user=notification.user)
    url = _get_notification_url(notification)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
