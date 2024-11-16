from django.db import models

from app.content.models.user import User
from app.util.models import BaseModel
from django.utils.timezone import now, timedelta


def now_plus_5_minutes():
    return now + timedelta(minutes=5)


class OAuthApps(BaseModel):
    client_id = models.CharField(max_length=255, unique=True, primary_key=True)
    app_name = models.CharField(max_length=50)
    image = models.URLField(max_length=600, null=True, blank=True)

    # TODO: Hash this field with sha256 later
    client_secret = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.app_name}"


class OAuthRequest(BaseModel):
    auth_code = models.CharField(max_length=255, unique=True)
    client_id = models.ForeignKey(OAuthApps, on_delete=models.CASCADE)
    user_token = models.CharField(max_length=255, blank=True)
    expires = models.DateTimeField(default=now_plus_5_minutes)
