from django.db import models

from app.codex.enums import CodexGroups
from app.codex.models.event import CodexEvent
from app.codex.util import user_is_leader_of_codex_group
from app.common.permissions import BasePermissionModel
from app.content.models import User
from app.util.models import BaseModel


class CodexEventRegistration(BaseModel, BasePermissionModel):
    read_access = CodexGroups.all()
    write_access = CodexGroups.all()

    registration_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="codex_event_registrations"
    )
    event = models.ForeignKey(
        CodexEvent, on_delete=models.CASCADE, related_name="codex_event_registrations"
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ("order", "created_at")
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user} - {self.event.title} - {self.created_at}"

    @classmethod
    def has_update_permission(cls, request):
        return cls.has_write_permission(request)

    @classmethod
    def has_destroy_permission(cls, request):
        return cls.has_write_permission(request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return cls.has_read_permission(request)

    def has_object_update_permission(self, request):
        user = request.user
        return user == self.user or user_is_leader_of_codex_group(user)

    def has_object_destroy_permission(self, request):
        user = request.user
        return user == self.user or user_is_leader_of_codex_group(user)

    def has_object_retrieve_permission(self, request):
        return self.has_retrieve_permission(request)
