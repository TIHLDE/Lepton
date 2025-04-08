from django.urls import path

from app.apikey.views import send_email, upload

urlpatterns = [
    path("upload/", upload, name="upload"),
    path("email/", send_email, name="send_email"),
]
