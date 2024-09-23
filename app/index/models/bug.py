from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models.user import User
from app.index.enums import Status
from app.util.models import BaseModel


class Bug(BaseModel, BasePermissionModel):
    read_access = (Groups.TIHLDE,)
    write_access = (Groups.TIHLDE,)

    title = models.CharField(max_length=100)
    description = models.TextField(default="", blank=True)

    author = models.ForeignKey(
        User, blank=True, null=True, default=None, on_delete=models.SET_NULL
    )
    status = models.CharField(Status.choices, default=Status.OPEN, max_length=20)

    def __str__(self):
        return f"{self.title} - {self.status}"


class Meta:
    ordering = ("created_at",)


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
        self.check_has_access([AdminGroup.INDEX], request)
        or self.author == request.user
    )


def has_object_destroy_permission(self, request):
    return (
        self.check_has_access([AdminGroup.INDEX], request)
        or self.author == request.user
    )
