from django.db import models

from app.blitzed.models.session import Session
from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.util.models import BaseModel


class UserWastedLevel(BaseModel, BasePermissionModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    blood_alcohol_level = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"WastedLevel - User: {self.user}, Session: {self.session}, Level: {self.blood_alcohol_level}"

    class Meta:
        verbose_name_plural = "User Wasted Levels"
