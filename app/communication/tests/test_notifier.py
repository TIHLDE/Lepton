from unittest.mock import patch

import pytest

from app.communication.enums import UserNotificationSettingType
from app.communication.factories import UserNotificationSettingFactory
from app.communication.models.mail import Mail
from app.communication.models.notification import Notification
from app.communication.notifier import Notify
from app.content.factories import UserFactory


@pytest.mark.django_db
def test_email_is_created_only_when_wanted():
    """
    Email should be created only for users who want to recieve email for the specified notification_type.
    Users with email=True or those who haven't set the setting should recieve a email.
    """

    assert Mail.objects.count() == 0

    NOTIFICATION_TYPE = UserNotificationSettingType.EVENT_INFO

    setting1 = UserNotificationSettingFactory(
        email=True, notification_type=NOTIFICATION_TYPE
    )
    setting2 = UserNotificationSettingFactory(
        email=False, notification_type=NOTIFICATION_TYPE
    )
    user1 = setting1.user
    user2 = setting2.user
    user3 = UserFactory()

    Notify([user1, user2, user3], "Test mail", NOTIFICATION_TYPE).add_paragraph(
        "This is a test"
    ).send()

    assert Mail.objects.count() == 1
    sent_email_users = Mail.objects.first().users.all()
    assert user1 in sent_email_users
    assert user2 not in sent_email_users
    assert user3 in sent_email_users


@pytest.mark.django_db
def test_notification_is_created_only_when_wanted():
    """
    Notification should be created only for users who want to recieve notification on the website for the specified notification_type.
    Users with website=True or those who haven't set the setting should recieve a notification.
    """

    assert Notification.objects.count() == 0

    NOTIFICATION_TYPE = UserNotificationSettingType.EVENT_INFO

    setting1 = UserNotificationSettingFactory(
        website=True, notification_type=NOTIFICATION_TYPE
    )
    setting2 = UserNotificationSettingFactory(
        website=False, notification_type=NOTIFICATION_TYPE
    )
    user1 = setting1.user
    user2 = setting2.user
    user3 = UserFactory()

    Notify([user1, user2, user3], "Test notification", NOTIFICATION_TYPE).add_paragraph(
        "This is a test"
    ).send()

    assert Notification.objects.count() == 2
    assert Notification.objects.filter(user=user1).exists()
    assert not Notification.objects.filter(user=user2).exists()
    assert Notification.objects.filter(user=user3).exists()


@pytest.mark.django_db
@patch("app.communication.slack.Slack.send")
def test_slack_message_is_sent_only_when_wanted(mock_slack_message):
    """
    Slack message should only be sent to users who want to recieve Slack messages for the specified notification_type.
    Users with slack=True or those who haven't set the setting should recieve a Slack message.
    """

    NOTIFICATION_TYPE = UserNotificationSettingType.EVENT_INFO

    # Should recieve Slack message:
    user1 = UserFactory(slack_user_id="12")
    UserNotificationSettingFactory(
        slack=True, notification_type=NOTIFICATION_TYPE, user=user1
    )
    user2 = UserFactory(slack_user_id="34")

    # Should not recieve Slack message:
    user3 = UserFactory(slack_user_id="56")
    UserNotificationSettingFactory(
        slack=False, notification_type=NOTIFICATION_TYPE, user=user3
    )
    user4 = UserFactory(slack_user_id="")

    Notify(
        [user1, user2, user3, user4], "Test notification", NOTIFICATION_TYPE
    ).add_paragraph("This is a test").send()

    assert mock_slack_message.call_count == 2
