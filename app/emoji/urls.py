from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.emoji.views.custom_emoji import CustomEmojiViewSet
from app.emoji.views.reaction import ReactionViewSet
from app.emoji.views.unicode_emoji import UnicodeEmojiViewSet

router = routers.DefaultRouter()

router.register("custom", CustomEmojiViewSet, basename="custom")
router.register("unicode", UnicodeEmojiViewSet, basename="unicode")
router.register("reaction", ReactionViewSet, basename="reaction")

urlpatterns = [
    path("", include(router.urls)),
]