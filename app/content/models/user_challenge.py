from django.db import models

from app.content.models import Challenge, User
from app.util.models import BaseModel


class UserChallenge(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "User Challenges"

    def __str__(self):
        return self.challenge.title + " - " + self.user.user_id
