import os

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from sentry_sdk import capture_exception

from app.util.utils import chunk_list


class Notify:
    def __init__(self, users, title):
        """
        users: User[] -> The users to be notified\n
        title: str -> Title of the notification
        """
        self.users = users
        self.title = title

    def send_email(self, html, subject=None):
        """
        html: str -> The email HTML to be sent to the users\n
        subject: str -> Subject of email, defaults to given title\n
        """
        from app.communication.models.mail import Mail

        if subject is None:
            subject = self.title

        if len(self.users) > 0:
            mail = Mail.objects.create(subject=subject, body=html)

            for user in self.users:
                mail.users.add(user)

        return self

    def send_notification(self, title=None, description=None, link=None):
        """
        title: str -> Title in notification, defaults to given title
        description: str -> Description in notification, defaults to blank string
        link: str -> Link in notification, optional
        """
        from app.content.models.notification import Notification

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


def send_html_email(to_mails, html, subject):
    """
    to_mails: str -> Email-addresses of receivers\n
    html: str -> The email HTML to be sent to the receivers\n
    subject: str -> Subject of email\n

    returns: bool -> If the mails where sent successfully
    """

    MAX_EMAILS_PER_SENDING = 100

    is_success = True
    for mails in chunk_list(to_mails, MAX_EMAILS_PER_SENDING):
        try:
            text_content = strip_tags(html)
            email_sender = os.environ.get("EMAIL_USER")
            msg = EmailMultiAlternatives(
                subject, text_content, f"TIHLDE <{email_sender}>", bcc=mails
            )
            msg.attach_alternative(html, "text/html")
            result = msg.send()
            if result == 0:
                is_success = False
        except Exception as send_mail_fail:
            capture_exception(send_mail_fail)
            is_success = False

    return is_success
