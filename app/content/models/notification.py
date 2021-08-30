from django.db import models

from app.util.models import BaseModel


class Notification(BaseModel):
    user = models.ForeignKey("content.User", on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField(default="", blank=True)
    link = models.CharField(max_length=150, blank=True, null=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user}, title: {self.title}, description: {self.description}"

    @classmethod
    def has_read_permission(cls, request):
        return request.user is not None

    def has_object_read_permission(self, request):
        if request.user is None:
            return False
        return self.user == request.user

    @classmethod
    def has_write_permission(cls, request):
        if request.user is None:
            return False
        return request.method == "PUT"

    def has_object_write_permission(self, request):
        if request.user is None:
            return False
        if request.method == "PUT":
            return self.user == request.user
        return False

