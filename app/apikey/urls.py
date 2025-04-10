from django.urls import path

from app.apikey.views import send, upload

urlpatterns = [
    path("upload/", upload, name="upload"),
    path("email/", send, name="send_email"),
]
