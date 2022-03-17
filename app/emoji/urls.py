from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.emoji.views import CustomEmojiViewSet
from app.emoji.views.unicode_emoji import UnicodeEmojiViewSet

router = routers.DefaultRouter()

router.register("custom", CustomEmojiViewSet, basename="custom")
router.register("unicode", UnicodeEmojiViewSet, basename="unicode")

urlpatterns = [
    path("", include(router.urls)),
]
