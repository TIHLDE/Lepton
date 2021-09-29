import os

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from celery import shared_task
from sentry_sdk import capture_exception

from app.common.enums import EnvironmentOptions
from app.content.models.notification import Notification


class Notify:
    def __init__(self, users, title):
        """
        users: User[] -> The users to be notified\n
        title: str -> Title of the notification
        """
        self.users = users
        self.title = title

    def send_email(self, html, subject=None, send_async=True):
        """
        html: str -> The email HTML to be sent to the users\n
        subject: str -> Subject of email, defaults to given title\n
        send_async: bool -> Should the email be sent asynchronous
        """
        if subject is None:
            subject = self.title

        emails = (user.email for user in self.users)
        send_html_email(emails, html, subject, send_async)

        return self

    def send_notification(self, title=None, description=None, link=None):
        """
        title: str -> Title in notification, defaults to given title
        description: str -> Description in notification, defaults to blank string
        link: str -> Link in notification, optional
        """
        if title is None:
            title = self.title
        if description is None:
            description = ""

        bulk_inserts = []

        for user in self.users:
            bulk_inserts.append(
                Notification(user=user, title=title, description=description, link=link)
            )

        if bulk_inserts:
            Notification.objects.bulk_create(bulk_inserts, batch_size=1000)

        return self


def send_html_email(to_mails, html, subject, send_async=True):
    if (
        settings.ENVIRONMENT == EnvironmentOptions.PRODUCTION
        or settings.ENVIRONMENT == EnvironmentOptions.DEVELOPMENT
    ) and send_async:
        __send_email.apply_async((to_mails, html, subject))
    else:
        __send_email(to_mails, html, subject)


@shared_task
def __send_email(to_mails, html, subject):
    """
        to_mails: str -> Email-addresses of receivers\n
        html: str -> The email HTML to be sent to the users\n
        subject: str -> Subject of email
        """
    try:
        text_content = strip_tags(html)
        email_recipient = os.environ.get("EMAIL_USER")
        msg = EmailMultiAlternatives(
            subject, text_content, f"TIHLDE <{email_recipient}>", bcc=to_mails
        )
        msg.attach_alternative(html, "text/html")
        msg.send()
        return True
    except Exception as send_html_email_fail:
        capture_exception(send_html_email_fail)
        return False
