import uuid

from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.db.models import Q
from django.utils import timezone

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel, OptionalImage
from app.util.utils import now


class BannerManager(BaseUserManager):
    def visible(self):
        return Banner.objects.filter(
            Q(visible_from__lte=now()) & Q(visible_until__gte=now())
        )


def tomorrow():
    return timezone.now() + timezone.timedelta(days=1)


class Banner(BaseModel, OptionalImage, BasePermissionModel):
    write_access = AdminGroup.admin()

    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    visible_from = models.DateTimeField(default=timezone.now)
    visible_until = models.DateTimeField(default=tomorrow)
    url = models.URLField(max_length=400, blank=True, null=True)

    objects = BannerManager()

    def __str__(self):
        return f"{self.title} is {'' if self.is_visible else 'not'} visible"

    def save(self, *args, **kwargs):
        if self.is_visible and not self.is_uniquely_visible:
            raise ValueError("Finnes allerede et banner som er synlig")
        if self.visible_from > self.visible_until:
            raise ValueError("Datoer er satt feil")
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-updated_at",)

    @property
    def is_visible(self):
        return self.visible_from <= now() and self.visible_until >= now()

    @property
    def is_uniquely_visible(self):
        return not Banner.objects.visible().exclude(id=self.id).exists()
