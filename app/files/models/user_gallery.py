from django.db import models
from django.db.models import PROTECT

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models.user import User
from app.util.models import BaseModel


class UserGallery(BaseModel, BasePermissionModel):
    read_access = AdminGroup.admin()
    write_access = AdminGroup.admin()

    author = models.OneToOneField(
        User, on_delete=PROTECT, related_name="user_galleries"
    )

    class Meta:
        pass

    def __str__(self):
        return f"Gallery by {self.author.first_name} {self.author.last_name}"

    @classmethod
    def has_read_permission(cls, request):
        return super().has_read_permission(request)

    @classmethod
    def has_write_permission(cls, request):
        return super().has_write_permission(request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return cls.has_read_permission(request)

    @classmethod
    def has_create_permission(cls, request):
        return cls.has_write_permission(request)

    @classmethod
    def has_update_permission(cls, request):
        return cls.has_write_permission(request)

    @classmethod
    def has_destroy_permission(cls, request):
        return cls.has_write_permission(request)

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
        return (
            check_has_access(self.write_access, request) and self.author == request.user
        )

    def has_object_destroy_permission(self, request):
        return (
            check_has_access(self.write_access, request) and self.author == request.user
        )

    @classmethod
    def get_all_files(cls, user):
        return cls.objects.get(author=user).files.all()

    @classmethod
    def has_gallery(cls, user):
        return cls.objects.filter(author=user).exists()

    @classmethod
    def create_gallery(cls, user):
        return cls.objects.create(author=user)
