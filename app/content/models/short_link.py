from django.db import models
from django.utils.text import slugify

from app.common.enums import Groups
from app.common.perm import BasePermissionModel, get_user_from_request, get_user_id
from app.content.models import User
from app.util.models import BaseModel


class ShortLink(BaseModel, BasePermissionModel):
    name = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="short_links")
    url = models.URLField(max_length=600)

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

    def has_object_write_permission(self, request):
        if self.user.user_id == get_user_id(request):
            return True
        return super().has_object_write_permission(request)
