import os
from unittest.mock import patch

from rest_framework import status

import pytest

from app.communication.enums import UserNotificationSettingType
from app.communication.notifier import Notify
from app.content.factories import UserFactory
from app.util.test_utils import get_api_client

EMAIL_URL = "/send-email/"
EMAIL_API_KEY = os.environ.get("EMAIL_API_KEY")


def _get_email_url():
    return f"{EMAIL_URL}"


@pytest.mark.django_db
@patch.object(Notify, "send", return_value=None)
def test_send_email_success(mock_send):
    """
    Test that the send_email endpoint sends an email successfully.
    """
    test_user = UserFactory()

    data = {
        "user_id_list": [test_user.user_id],
        "notification_type": "KONTRES",
        "title": "Test Notification",
        "paragraphs": ["This is a test paragraph.", "This is another paragraph."],
    }

    client = get_api_client(user=test_user)
    url = _get_email_url()
    headers = {"api_key": EMAIL_API_KEY}
    response = client.post(url, data, format="json", **headers)

    assert response.status_code == status.HTTP_201_CREATED
    mock_send.assert_called_once()


@pytest.mark.django_db
@patch.object(Notify, "send", return_value=None)
def test_send_email_fails_when_field_missing(mock_send):
    """
    Test that the send_email endpoint returns 400 when one of the fields is missing.
    """
    test_user = UserFactory()

    data = {
        "user_id_list": [test_user.user_id],
        "title": "Test Notification",
        "paragraphs": ["This is a test paragraph.", "This is another paragraph."],
    }

    client = get_api_client(user=test_user)
    url = _get_email_url()
    headers = {"api_key": EMAIL_API_KEY}
    response = client.post(url, data, format="json", **headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_send.assert_not_called()


@pytest.mark.django_db
@patch.object(Notify, "send", return_value=None)
def test_send_email_fails_when_wrong_api_key(mock_send):
    """
    Test that the send_email endpoint returns 403 when the API key is invalid.
    """
    test_user = UserFactory()

    data = {
        "user_id_list": [test_user.user_id],
        "notification_type": "KONTRES",
        "title": "Test Notification",
        "paragraphs": ["This is a test paragraph.", "This is another paragraph."],
    }

    client = get_api_client(user=test_user)
    url = _get_email_url()
    headers = {"api_key": "wrong_key"}
    response = client.post(url, data, format="json", **headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_send.assert_not_called()


@pytest.mark.django_db
@patch.object(Notify, "send", return_value=None)
def test_send_email_fails_when_user_id_invalid(mock_send):
    """
    Test that the send_email endpoint returns 404 when the user id is invalid.
    """
    test_user = UserFactory()

    data = {
        "user_id_list": [999],
        "notification_type": "KONTRES",
        "title": "Test Notification",
        "paragraphs": ["This is a test paragraph.", "This is another paragraph."],
    }

    client = get_api_client(user=test_user)
    url = _get_email_url()
    headers = {"api_key": EMAIL_API_KEY}
    response = client.post(url, data, format="json", **headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_send.assert_not_called()


@pytest.mark.django_db
@patch.object(Notify, "send", return_value=None)
@pytest.mark.parametrize(
    "notification_type", UserNotificationSettingType.get_kontres_and_blitzed()
)
def test_email_success_with_kontres_and_blitzed(mock_send, notification_type):
    """
    Tests that the send_email endpoint works with both KONTRES and BLITZED notification types.
    """
    test_user = UserFactory()

    data = {
        "user_id_list": [test_user.user_id],
        "notification_type": notification_type,
        "title": "Test Notification",
        "paragraphs": ["This is a test paragraph.", "This is another paragraph."],
    }

    client = get_api_client(user=test_user)
    url = _get_email_url()
    headers = {"api_key": EMAIL_API_KEY}
    response = client.post(url, data, format="json", **headers)

    assert response.status_code == status.HTTP_201_CREATED
    mock_send.assert_called_once()
