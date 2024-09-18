from django.db import models

from app.codex.enums import CodexCourseTags, CodexGroups
from app.codex.util import user_is_leader_of_codex_group
from app.common.permissions import BasePermissionModel
from app.content.models import User
from app.group.models import Group
from app.util.models import BaseModel


class Course(BaseModel, BasePermissionModel):
    read_access = CodexGroups.all()
    write_access = CodexGroups.all()

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")

    start_date = models.DateTimeField()

    start_registration_at = models.DateTimeField(blank=True, null=True, default=None)
    end_registration_at = models.DateTimeField(blank=True, null=True, default=None)

    tag = models.CharField(
        max_length=50, choices=CodexCourseTags.choices, default=CodexCourseTags.LECTURE
    )

    location = models.CharField(max_length=200, null=True)
    mazemap_link = models.URLField(max_length=2000, null=True)

    organizer = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="codex_courses",
    )
    lecturer = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="codex_courses",
    )

    registrations = models.ManyToManyField(
        User,
        through="CourseRegistration",
        through_fields=("course", "user"),
        blank=True,
        default=None,
    )

    class Meta:
        verbose_name_plural = "Courses"
        ordering = ("start_date",)

    def __str__(self):
        return f"{self.title} - starting {self.start_date} at {self.location}"

    @property
    def list_count(self):
        return self.registrations.count()

    @classmethod
    def has_write_permission(cls, request):
        user = request.user
        return user_is_leader_of_codex_group(user)

    @classmethod
    def has_update_permission(cls, request):
        return cls.has_write_permission(request)

    @classmethod
    def has_destroy_permission(cls, request):
        return cls.has_write_permission(request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return cls.has_read_permission(request)

    def has_object_write_permission(self, request):
        return self.has_write_permission(request)

    def has_object_update_permission(self, request):
        return self.has_write_permission(request)

    def has_object_destroy_permission(self, request):
        return self.has_write_permission(request)

    def has_object_retrieve_permission(self, request):
        return self.has_read_permission(request)
