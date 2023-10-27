from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.emoji.views.custom_emoji import CustomEmojiViewSet
from app.emoji.views.reaction import ReactionViewSet

router = routers.DefaultRouter()

router.register("custom", CustomEmojiViewSet, basename="custom")
router.register("reactions", ReactionViewSet, basename="reactions")

urlpatterns = [
    path("", include(router.urls)),
]
