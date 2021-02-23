from app.common.enums import AdminGroup
from django.db import models
from app.common.perm import BasePermissionModel
from app.util.models import BaseModel, OptionalImage


class News(BaseModel, OptionalImage, BasePermissionModel):
    title = models.CharField(max_length=200)
    header = models.CharField(max_length=200)
    body = models.TextField()
    
    read_access = [AdminGroup.INDEX]

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return f"{self.title} - {self.header} ({len(self.body)} characters)"
