from django.db import models

from app.util.models import BaseModel


class Notification(BaseModel):
    user = models.ForeignKey("content.User", on_delete=models.CASCADE)
    message = models.CharField(max_length=150)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user}"

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


def create_notification(user, message):
    return Notification.objects.create(user=user, message=message)
