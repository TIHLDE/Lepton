import uuid

from django.db import models

from app.content.models.badge_category import BadgeCategory
from app.util.models import BaseModel, OptionalImage
from app.util.utils import now


class Badge(BaseModel, OptionalImage):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    flag = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    badge_category = models.ForeignKey(
        BadgeCategory, on_delete=models.SET_NULL, null=True, default=None, blank=True
    )
    active_from = models.DateTimeField(blank=True, null=True)
    active_to = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Badges"

    def __str__(self):
        return f"{self.title} - {self.description}"

    def save(self, *args, **kwargs):
        if len(self.flag) == 0:
            self.flag = str(self.id)
        super().save(*args, **kwargs)

    @property
    def active(self):
        _now = now()
        if self.active_from is None and self.active_to is None:
            return True
        if self.active_from is None:
            return _now <= self.active_to
        if self.active_to is None:
            return _now >= self.active_from
        return _now >= self.active_from and _now <= self.active_to

    @property
    def is_public(self):
        if self.active_to is None:
            return self.active
        return self.active_to <= now()
