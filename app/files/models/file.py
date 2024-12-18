from django.db import models
from django.db.models import PROTECT

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.files.models.user_gallery import UserGallery
from app.util.models import BaseModel, OptionalFile


class File(BaseModel, BasePermissionModel, OptionalFile):
    read_access = AdminGroup.admin()
    write_access = AdminGroup.admin()

    title = models.CharField(max_length=80)

    description = models.TextField(blank=True)
    gallery = models.ForeignKey(
        UserGallery, on_delete=PROTECT, related_name="files", blank=False
    )

    class Meta:
        pass

    def __str__(self):
        return self.title

    @classmethod
    def has_read_permission(cls, request):
        return super().has_read_permission(request)

    @classmethod
    def has_write_permission(cls, request):
        return check_has_access(Groups.TIHLDE, request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return cls.has_read_permission(request)

    @classmethod
    def has_create_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_update_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_destroy_permission(cls, request):
        return check_has_access(Groups.TIHLDE, request)

    @classmethod
    def has_list_permission(cls, request):
        return cls.has_read_permission(request)

    def has_object_read_permission(self, request):
        return self.has_read_permission(request)

    def has_object_write_permission(self, request):
        return self.has_write_permission(request)

    def has_object_retrieve_permission(self, request):
        return self.has_object_read_permission(request)

    def has_object_update_permission(self, request):
        return self.gallery.author == request.user

    def has_object_destroy_permission(self, request):
        return self.gallery.author == request.user
