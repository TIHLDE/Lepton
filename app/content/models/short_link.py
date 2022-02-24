from django.db import models
from django.utils.text import slugify

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models import User
from app.util.models import BaseModel


class ShortLink(BaseModel, BasePermissionModel):
    name = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="short_links")
    url = models.URLField(max_length=600)
    write_access = [Groups.TIHLDE]

    class Meta:
        verbose_name = "Short link"
        verbose_name_plural = "Short links"

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.user.user_id}"

    @classmethod
    def has_create_permission(cls, request):
        cls.write_access = [Groups.TIHLDE]
        return super().has_write_permission(request)

    @classmethod
    def has_destroy_permission(cls, request):
        return True

    def has_object_write_permission(self, request):
        return self.user == request.user or super().has_object_write_permission(request)
