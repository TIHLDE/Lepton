from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.emoji.models.reaction import Reaction
from app.util.models import BaseModel, OptionalImage


class News(BaseModel, OptionalImage, BasePermissionModel):
    title = models.CharField(max_length=200)
    header = models.CharField(max_length=200)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_news",
    )
    body = models.TextField()
    emojis_allowed = models.BooleanField(default=False)
    reactions = GenericRelation(Reaction)

    write_access = [*AdminGroup.all(), Groups.FONDET]

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return f"{self.title} - {self.header} ({len(self.body)} characters)"

    @property
    def website_url(self):
        return f"/nyheter/{self.id}/"

    @classmethod
    def has_write_permission(cls, request):
        if not request.user:
            return False
        return request.user.is_leader_of_committee or check_has_access(
            cls.write_access, request
        )
