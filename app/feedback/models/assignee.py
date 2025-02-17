from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models.user import User
from app.feedback.models.feedback import Feedback
from app.util.models import BaseModel


class Assignee(BaseModel, BasePermissionModel):
    write_access = (AdminGroup.INDEX,)
    read_access = (Groups.TIHLDE,)

    assignee_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignees")
    feedback = models.ForeignKey(
        Feedback, on_delete=models.CASCADE, related_name="assignee_feedbacks"
    )

    def __str__(self):
        return f"{self.user.first_name} - {self.feedback.title}"

    class Meta:
        ordering = ("feedback", "created_at")
        unique_together = ("user", "feedback")
        verbose_name = "Assignee"
        verbose_name_plural = "Assignees"

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
            check_has_access([AdminGroup.INDEX], request) and self.user == request.user
        )

    def has_object_destroy_permission(self, request):
        return (
            check_has_access([AdminGroup.INDEX], request) and self.user == request.user
        )
