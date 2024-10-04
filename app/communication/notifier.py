import os
from typing import Optional

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from sentry_sdk import capture_exception

from app.communication.enums import UserNotificationSettingType
from app.communication.slack import Slack
from app.content.models.user import User
from app.util.mail_creator import MailCreator
from app.util.utils import chunk_list


class Notify:
    def __init__(
        self,
        users: list[User],
        title: str,
        notification_type: UserNotificationSettingType,
    ):
        """
        users -> The users to be notified\n
        title -> Title of the notification\n
        notification_type -> Type of notification
        """
        self.users = users
        self.title = title
        self.notification_type = notification_type

        self.slack = Slack(title).add_header(title)
        self.mail = MailCreator(title)
        self.notification_title = title
        self.notification_description = []
        self.notification_link: Optional[str] = None

    def add_paragraph(self, text: str, mail=True, website=True, slack=True):
        """
        text -> The text in the paragraph
        """

        if mail:
            self.mail.add_paragraph(text)

        if website:
            self.notification_description.append(text)

        if slack:
            self.slack.add_paragraph(text)

        return self

    def add_link(self, text: str, link: str, mail=True, website=True, slack=True):
        """
        text -> The text on the button\n
        link -> The link to go to on click
        """

        if mail:
            self.mail.add_button(text, link)

        if website:
            self.notification_link = link

        if slack:
            self.slack.add_link(text, link)

        return self

    def add_event_link(self, event_id: int, mail=True, website=True, slack=True):
        """
        event_id -> Id of the event
        """

        if mail:
            self.mail.add_event_button(event_id)

        if website:
            self.notification_link = f"/arrangementer/{event_id}/"

        if slack:
            self.slack.add_event_link(event_id)

        return self

    def _send_mail(self):
        from app.communication.models.mail import Mail

        if len(self.users) > 0:
            mail = Mail.objects.create(
                subject=self.title, body=self.mail.generate_string()
            )

            for user in self.users:
                if not user.user_notification_settings.filter(
                    notification_type=self.notification_type, email=False
                ).exists():
                    mail.users.add(user)

    def _send_slack(self):
        for user in filter(lambda user: bool(user.slack_user_id), self.users):
            if not user.user_notification_settings.filter(
                notification_type=self.notification_type, slack=False
            ).exists():
                self.slack.send(user.slack_user_id)

    def _send_notification(self):
        from app.communication.models.notification import Notification

        bulk_inserts = []

        for user in self.users:
            if not user.user_notification_settings.filter(
                notification_type=self.notification_type, website=False
            ).exists():
                bulk_inserts.append(
                    Notification(
                        user=user,
                        title=self.notification_title,
                        description="\n\n".join(self.notification_description),
                        link=self.notification_link,
                    )
                )

        if bulk_inserts:
            Notification.objects.bulk_create(bulk_inserts, batch_size=1000)

    def send(self, mail=True, website=True, slack=True):
        """Send the created mails, notifications and Slack-messages"""
        if mail:
            self._send_mail()

        if website:
            self._send_notification()

        if slack:
            self._send_slack()


def send_html_email(
    to_mails: list[str],
    html: str,
    subject: str,
    attachments=None,
    connection=None,
) -> bool:
    """
    to_mails -> Email-addresses of receivers\n
    html -> The email HTML to be sent to the receivers\n
    subject -> Subject of email\n
    attachments -> File attachments
    connection -> Backend email connection to use with EmailMultiAlternatives. Creates a new one if none is provided.

    returns -> If the mails where sent successfully
    """

    max_emails_per_sending = 100

    is_success = True
    for mails in chunk_list(to_mails, max_emails_per_sending):
        try:
            text_content = strip_tags(html)
            email_sender = os.environ.get("EMAIL_USER")
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                f"TIHLDE <{email_sender}>",
                bcc=mails,
                attachments=attachments,
                connection=connection,
            )
            msg.attach_alternative(html, "text/html")
            result = msg.send()
            if result == 0:
                is_success = False
        except Exception as send_mail_fail:
            capture_exception(send_mail_fail)
            is_success = False

    return is_success
