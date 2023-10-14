from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models import User
from app.util.models import BaseModel, OptionalImage


class QRCode(BaseModel, OptionalImage, BasePermissionModel):
    write_access = (Groups.TIHLDE,)
    read_access = (Groups.TIHLDE,)

    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="qr_codes")
    url = models.URLField(max_length=600)

    class Meta:
        verbose_name = "qr_code"
        verbose_name_plural = "qr_codes"

    def __str__(self):
        return f"{self.name} - {self.user.user_id}"
