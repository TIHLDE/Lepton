import os

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

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
        try:
            text_content = strip_tags(html)
            msg = EmailMultiAlternatives(
                subject, text_content, os.environ.get("EMAIL_USER"), [self.user.email]
            )
            msg.attach_alternative(html, "text/html")
            msg.send()
        except Exception as send_html_email_fail:
            capture_exception(send_html_email_fail)

        return self

    def send_notification(self, message=None):
        """
        message: str -> Message in notification, defaults to given title
        """
        if message is None:
            message = self.title
        Notification(user=self.user, message=message).save()

        return self
