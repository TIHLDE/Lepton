from django.db import models

from .user import User


class NotificationManager(models.Manager):

    def create_for_all_users(self, *, message):
        notifications = [
            {
                'user': users.user_id,
                'message': message,
                'read': False
            } for users in User.objects.tihlde_members()
        ]

        notifications = super().bulk_create(notifications)
        return notifications

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=150)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user}"

    objects = NotificationManager()
