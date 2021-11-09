from django.conf import settings
from django.db import models

from app.common.permissions import BasePermissionModel
from app.content.models import News
from app.group.models import Group
from app.util.models import TimeStampedModel


class Status(models.TextChoices):
    SENT = "SENT", "Innsendt"
    REVIEWED = "REVIEWED", "Gjennomgått"
    APPROVED = "APPROVED", "Godkjent"
    REJECTED = "REJECTED", "Avslått"


# TODO: signal to notify group/leader on creation
class ContentRequest(TimeStampedModel, BasePermissionModel):
    preferred_publish_date = models.DateTimeField(editable=False)
    scheduled_publish_date = models.DateTimeField(editable=False)
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.SENT
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="content_requests",
    )
    recipient_group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="content_requests"
    )
    # TODO: is there a better solution to this? What about requests for JobPosts?
    subject_news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="+")
