import uuid

from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel, check_has_access
from app.gallery.models.album import Album
from app.util.models import BaseModel


class Picture(BaseModel, BasePermissionModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.URLField(max_length=400)
    title = models.CharField(max_length=100, blank=True)
    image_alt = models.CharField(max_length=100, blank=True)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    write_access = AdminGroup.all()

    def __str__(self):
        return self.image

    @classmethod
    def has_create_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_destroy_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_update_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_list_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return check_has_access(cls.read_access, request)

    def has_object_destroy_permission(self, request):
        return True

    def has_object_update_permission(self, request):
        return True

    def has_object_retrieve_permission(self, request):
        return True
