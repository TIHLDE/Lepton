from django.db import models

from app.util.models import BaseModel


class Submission(BaseModel):
    user = models.ForeignKey("content.User", on_delete=models.CASCADE)
    challenge = models.ForeignKey("ctf.Challenge", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "challenge")
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"

    def __str__(self):
        return f"{self.challenge.title} - {self.user.first_name} {self.user.last_name}"
