import uuid

from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.db.models import Q

from app.badge.models.badge_category import BadgeCategory
from app.util.models import BaseModel, OptionalImage
from app.util.utils import now


class BadgeManager(BaseUserManager):
    def public(self):
        return Badge.objects.filter(
            (Q(active_from__isnull=True) | Q(active_from__lte=now()))
            & (Q(active_to__isnull=True) | Q(active_to__lte=now()))
        )


class Badge(BaseModel, OptionalImage):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    flag = models.UUIDField(auto_created=True, default=uuid.uuid4, serialize=False,)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    badge_category = models.ForeignKey(
        BadgeCategory, on_delete=models.SET_NULL, null=True, default=None, blank=True
    )
    active_from = models.DateTimeField(blank=True, null=True)
    active_to = models.DateTimeField(blank=True, null=True)

    objects = BadgeManager()

    class Meta:
        verbose_name_plural = "Badges"

    def __str__(self):
        return f"{self.title} - {self.description}"

    @property
    def active(self):
        return (not self.active_from or self.active_from <= now()) and (
            not self.active_to or self.active_to >= now()
        )

    @property
    def is_public(self):
        return (not self.active_from or self.active_from <= now()) and (
            not self.active_to or self.active_to <= now()
        )
