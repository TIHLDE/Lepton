from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.emoji.views import CustomEmojiViewSet
from app.emoji.views.unicode_emoji import UnicodeEmojiViewSet
from app.emoji.views.user_news_reaction import UserNewsReactionViewSet 

router = routers.DefaultRouter()

router.register("custom", CustomEmojiViewSet, basename="custom")
router.register("unicode", UnicodeEmojiViewSet, basename="unicode")
router.register("reactions", UserNewsReactionViewSet, basename="reactions")

urlpatterns = [
    path("", include(router.urls)),
]
