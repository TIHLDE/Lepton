from django.db import models

from app.common.enums import AdminGroup
from app.common.perm import BasePermissionModel
from app.util.models import BaseModel, OptionalImage
from app.util.utils import yesterday


class JobPost(BaseModel, OptionalImage, BasePermissionModel):
    title = models.CharField(max_length=200)
    ingress = models.CharField(max_length=800, blank=True, default="")
    body = models.TextField(blank=True, default="")
    location = models.CharField(max_length=200)

    deadline = models.DateTimeField(null=True, blank=True)
    is_continuously_hiring = models.BooleanField(default=False)

    company = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    link = models.URLField(max_length=300, blank=True, null=True)

    write_access = [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK]

    @property
    def expired(self):
        return self.deadline <= yesterday()

    def __str__(self):
        return f"JobPost: {self.company}  - {self.title}"
