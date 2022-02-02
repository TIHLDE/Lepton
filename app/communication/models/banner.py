import uuid

from django.db import models
from django.utils import timezone

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel, OptionalImage
from app.util.utils import now


class Banner(BaseModel, OptionalImage, BasePermissionModel):
    write_access = AdminGroup.admin()
    read_access = AdminGroup.admin()
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    visible_from = models.DateTimeField(default=timezone.now)
    visible_until = models.DateTimeField(blank=True, null=True)
    url = models.URLField(max_length=400, blank=True, null=True)

    def __str__(self):
        return f"{self.title} is {'' if self.is_visible else 'not'} visible"

    class Meta:
        ordering = ("-updated_at",)

    @property
    def is_visible(self):
        if self.visible_until:
            return now() >= self.visible_from and now() <= self.visible_until
        return now() >= self.visible_from
