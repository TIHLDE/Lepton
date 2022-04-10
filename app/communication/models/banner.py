import uuid

from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.communication.exceptions import (
    AnotherVisibleBannerError,
    DatesMixedError,
)
from app.communication.mixins import APIBannerErrorsMixin
from app.util.models import BaseModel, OptionalImage
from app.util.utils import now, tomorrow


class Banner(BaseModel, OptionalImage, BasePermissionModel, APIBannerErrorsMixin):
    write_access = AdminGroup.admin()
    read_access = AdminGroup.admin()

    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        serialize=False,
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    visible_from = models.DateTimeField(default=now)
    visible_until = models.DateTimeField(default=tomorrow)
    url = models.URLField(max_length=600, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.description}"

    def save(self, *args, **kwargs):
        if self.exists_overlapping_banners:
            raise AnotherVisibleBannerError(
                "Det finnes allerede et banner som er synlig for den tiden"
            )
        if self.visible_from > self.visible_until:
            raise DatesMixedError(
                "Datoen banneret er synlig til er satt etter datoen banneret for synlig fra. Bytt om disse to"
            )
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-updated_at",)

    @property
    def exists_overlapping_banners(self):
        return (
            Banner.objects.filter(
                visible_from__lte=self.visible_until,
                visible_until__gte=self.visible_from,
            )
            .exclude(id=self.id)
            .exists()
        )

    @classmethod
    def has_visible_permission(cls, request):
        return True
