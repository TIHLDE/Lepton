import os
from typing import Optional

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from sentry_sdk import capture_exception

from app.communication.enums import UserNotificationSettingType
from app.communication.slack import Slack
from app.content.models.user import User
from app.util.utils import chunk_list


class Notify:
    def __init__(
        self,
        users: list[User],
        title: str,
        notificationType: UserNotificationSettingType,
    ):
        """
        users -> The users to be notified\n
        title -> Title of the notification
        """
        self.users = users
        self.title = title
        self.notificationType = notificationType

    def send_email(self, html: str, subject: Optional[str] = None):
        """
        html -> The email HTML to be sent to the users\n
        subject -> Subject of email, defaults to given title
        """
        from app.communication.models.mail import Mail

        if subject is None:
            subject = self.title

        if len(self.users) > 0:
            mail = Mail.objects.create(subject=subject, body=html)

            for user in self.users:
                if not user.user_notification_settings.filter(
                    notification_type=self.notificationType, email=False
                ).exists():
                    mail.users.add(user)

        return self

    def send_slack(self, slack: Slack):
        """
        slack -> A Slack-object with the content to be sent to each user
        """
        for user in filter(lambda user: bool(user.slack_user_id), self.users):
            if not user.user_notification_settings.filter(
                notification_type=self.notificationType, slack=False
            ).exists():
                slack.send(user.slack_user_id)

        return self

    def send_notification(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        link: Optional[str] = None,
    ):
        """
        title -> Title in notification, defaults to given title\n
        description -> Description in notification, defaults to blank string\n
        link -> Link in notification, optional
        """
        from app.communication.models.notification import Notification

        if title is None:
            title = self.title
        if description is None:
            description = ""

        bulk_inserts = []

        for user in self.users:
            if not user.user_notification_settings.filter(
                notification_type=self.notificationType, website=False
            ).exists():
                bulk_inserts.append(
                    Notification(
                        user=user, title=title, description=description, link=link
                    )
                )

        if bulk_inserts:
            Notification.objects.bulk_create(bulk_inserts, batch_size=1000)

        return self


def send_html_email(
    to_mails: list[str], html: str, subject: str, attachments=None
) -> bool:
    """
    to_mails -> Email-addresses of receivers\n
    html -> The email HTML to be sent to the receivers\n
    subject -> Subject of email\n

    returns -> If the mails where sent successfully
    """

    MAX_EMAILS_PER_SENDING = 100

    is_success = True
    for mails in chunk_list(to_mails, MAX_EMAILS_PER_SENDING):
        try:
            text_content = strip_tags(html)
            email_sender = os.environ.get("EMAIL_USER")
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                f"TIHLDE <{email_sender}>",
                bcc=mails,
                attachments=attachments,
            )
            msg.attach_alternative(html, "text/html")
            result = msg.send()
            if result == 0:
                is_success = False
        except Exception as send_mail_fail:
            capture_exception(send_mail_fail)
            is_success = False

    return is_success
