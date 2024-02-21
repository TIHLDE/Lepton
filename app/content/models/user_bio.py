from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models.user import User
from app.util.models import BaseModel


class UserBio(BaseModel, BasePermissionModel):
    read_access = (Groups.TIHLDE,)
    write_access = (Groups.TIHLDE,)

    description = models.CharField(max_length=50, blank=True, null=True)

    gitHub_link = models.URLField(max_length=300, blank=True, null=True)

    linkedIn_link = models.URLField(max_length=300, blank=True, null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, related_name="bio")

    def __str__(self):
        bio_str = f"{self.user}"
        if self.description:
            bio_str += f" - {self.description}"
        if self.gitHub_link:
            bio_str += f" - {self.gitHub_link}"
        if self.linkedIn_link:
            bio_str += f" - {self.linkedIn_link}"
        return bio_str

    @classmethod
    def has_update_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_destroy_permission(cls, request):
        return check_has_access(cls.write_access, request)

    def has_object_update_permission(self, request):
        return self.user == request.user

    def has_object_destroy_permission(self, request):
        return self.user == request.user
