import uuid

from django.db import models
from django.utils.timezone import now

from app.content.models import User
from app.util.models import BaseModel


class Mail(BaseModel):
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
    )

    eta = models.DateTimeField(default=now)
    subject = models.CharField(max_length=200)
    body = models.TextField(default="")
    users = models.ManyToManyField(User, related_name="emails", blank=True)

    class Meta:
        verbose_name = "Mail"
        verbose_name_plural = "Mails"
        ordering = ["-eta"]

    def send(self, connection):
        from app.communication.notifier import send_html_email

        emails = [user.email for user in self.users.all()]
        is_success = send_html_email(
            to_mails=emails,
            html=self.body,
            subject=self.subject,
            connection=connection,
        )
        if is_success:
            self.delete()

        return is_success

    def __str__(self):
        return (
            f"\"{self.subject}\", to {self.users.all()[0] if self.users.count() == 1 else f'{self.users.count()} users'}, "
            f"{'sent' if self.sent else 'eta'} {self.eta}"
        )
