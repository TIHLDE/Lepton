from rest_framework import status

import pytest

from app.communication.enums import UserNotificationSettingType
from app.util.test_utils import get_api_client

USER_NOTIFICATION_SETTING_URL = "/notification-settings/"


def _get_user_notification_setting_post_data(user_notification_setting=None):
    return {
        "email": True,
        "website": True,
        "slack": True,
        "notification_type": (
            user_notification_setting.notification_type
            if user_notification_setting
            else UserNotificationSettingType.EVENT_SIGN_OFF_DEADLINE
        ),
    }


@pytest.mark.django_db
def test_list_user_notification_settings_as_anonymous_user_fails(default_client):
    """Tests if an anonymous user can list notification settings"""

    response = default_client.get(USER_NOTIFICATION_SETTING_URL)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_user_notification_settings_as_user(member):
    """Tests if an logged in user can list notification settings"""

    client = get_api_client(user=member)
    response = client.get(USER_NOTIFICATION_SETTING_URL)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_user_notification_setting_as_anonymous(default_client):
    """An anonymous user should not be able to create a notification setting"""
    response = default_client.post(
        USER_NOTIFICATION_SETTING_URL, _get_user_notification_setting_post_data()
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_user_notification_setting_as_user(member):
    """A logged in user should be able to create a notification setting"""
    client = get_api_client(user=member)
    response = client.post(
        USER_NOTIFICATION_SETTING_URL, _get_user_notification_setting_post_data()
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_post_user_notification_setting_updates_if_exists(user_notification_setting):
    """
    When posting notification setting, existing setting should be updated.
    No new setting should be created.
    """
    AMOUNT_OF_SETTINGS = 1

    client = get_api_client(user=user_notification_setting.user)
    initial_response = client.get(USER_NOTIFICATION_SETTING_URL)

    assert initial_response.status_code == status.HTTP_200_OK
    assert len(initial_response.json()) == AMOUNT_OF_SETTINGS

    NEW_SLACK_BOOL = False
    data = _get_user_notification_setting_post_data(user_notification_setting)
    data["slack"] = NEW_SLACK_BOOL

    response = client.post(USER_NOTIFICATION_SETTING_URL, data)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == AMOUNT_OF_SETTINGS
    assert response.json()[0]["slack"] == NEW_SLACK_BOOL
