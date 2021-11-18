from django.db import models

from app.career.enums import JobPostType
from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.enums import UserClass
from app.util.models import BaseModel, OptionalImage
from app.util.utils import yesterday


class JobPost(BaseModel, OptionalImage, BasePermissionModel):
    title = models.CharField(max_length=200)
    ingress = models.CharField(max_length=800, blank=True, default="")
    body = models.TextField(blank=True, default="")
    location = models.CharField(max_length=200)

    deadline = models.DateTimeField(null=True, blank=True)
    is_continuously_hiring = models.BooleanField(default=False)
    job_type = models.CharField(
        max_length=30, choices=JobPostType.choices, default=JobPostType.OTHER
    )

    company = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    link = models.URLField(max_length=300, blank=True, null=True)

    class_start = models.IntegerField(
        choices=UserClass.choices, default=UserClass.FIRST
    )
    class_end = models.IntegerField(choices=UserClass.choices, default=UserClass.FIFTH)

    write_access = [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK]

    @property
    def expired(self):
        return self.deadline <= yesterday()

    def __str__(self):
        return f"JobPost: {self.company}  - {self.title}"

    @property
    def website_url(self):
        return f"/karriere/{self.id}/"
