from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.emoji.views import CustomEmojiViewSet

router = routers.DefaultRouter()

router.register("custom", CustomEmojiViewSet, basename="custom")

urlpatterns = [
    path("", include(router.urls)),
]
