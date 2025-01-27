from django.db import models

from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.feedback.models import Feedback
from app.util.models import BaseModel


class Assignee(BaseModel, BasePermissionModel):
    assignee_id = models.AutoField(primary_key=True)
    # TODO: check 'on delete'
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignees")
    feedback = models.ForeignKey(
        Feedback, on_delete=models.CASCADE, related_name="assignees"
    )

    class Meta:
        ordering = ("feedback", "created_at")
        unique_together = ("user", "feedback")
        verbose_name = "Assignee"
        verbose_name_plural = "Assignees"


    def __str__(self):
        return f"{self.user.first_name} - {self.feedback.title}"

