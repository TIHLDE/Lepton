from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel, OptionalImage
from app.content.models.comment import Comment

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

    write_access = [*AdminGroup.all(), Groups.FONDET]

    allow_comments = models.BooleanField(default=True)
    comments = GenericRelation(Comment)

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return f"{self.title} - {self.header} ({len(self.body)} characters)"

    @property
    def website_url(self):
        return f"/nyheter/{self.id}/"
