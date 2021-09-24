import os

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from celery import shared_task
from sentry_sdk import capture_exception

from app.content.models.notification import Notification


class Notify:
    def __init__(self, user, title):
        """
        user: User -> The user to be notified\n
        title: str -> Title of the notification
        """
        self.user = user
        self.title = title

    def send_email(self, html, subject=None):
        """
        html: str -> The email HTML to be sent to the user\n
        subject: str -> Subject of email, defaults to given title
        """
        if subject is None:
            subject = self.title

        send_html_email.apply_async((self.user.email, html, subject))

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
        Notification(
            user=self.user, title=title, description=description, link=link
        ).save()

        return self


@shared_task
def send_html_email(to_mail, html, subject):
    """
        to_mail: str -> Email-address of receiver\n
        html: str -> The email HTML to be sent to the user\n
        subject: str -> Subject of email
        """
    try:
        text_content = strip_tags(html)
        msg = EmailMultiAlternatives(
            subject, text_content, os.environ.get("EMAIL_USER"), [to_mail]
        )
        msg.attach_alternative(html, "text/html")
        msg.send()
        return True
    except Exception as send_html_email_fail:
        capture_exception(send_html_email_fail)
        return False
