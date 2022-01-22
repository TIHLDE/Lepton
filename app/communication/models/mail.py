from datetime import timedelta
import uuid

from django.db import models

from app.content.models import User
from app.util import now
from app.util.models import BaseModel

def default_time():
    """Default eta is in a minute"""
    return now() + timedelta(minutes=1)

class Mail(BaseModel):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4,
    )

    eta = models.DateTimeField(default=default_time)
    subject = models.CharField(max_length=200)
    body = models.TextField(default="")
    users = models.ManyToManyField(User, blank=True)
    sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Mail"
        verbose_name_plural = "Mails"
        ordering = ["-eta"]

    def __str__(self):
        return f"\"{self.subject}\", {self.users.all()[0] if self.users.count() == 1 else f'{self.users.count()} users'}, {'sent' if self.sent else 'eta'} {self.eta}"
