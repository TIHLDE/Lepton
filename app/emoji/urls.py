from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.emoji.views import CustomEmojiViewSet
from app.emoji.views.news_emojis import NewsEmojisViewSet
from app.emoji.views.toddel_emojis import ToddelEmojisViewSet
from app.emoji.views.unicode_emoji import UnicodeEmojiViewSet
from app.emoji.views.user_news_reaction import UserNewsReactionViewSet
from app.emoji.views.user_news_reaction_unicode import (
    UserNewsReactionUnicodeViewSet,
)
from app.emoji.views.user_toddel_reaction import UserToddelReactionViewSet
from app.emoji.views.user_toddel_reaction_unicode import (
    UserToddelReactionUnicodeViewSet,
)

router = routers.DefaultRouter()

router.register("custom", CustomEmojiViewSet, basename="custom")
router.register("unicode", UnicodeEmojiViewSet, basename="unicode")
router.register("reactions", UserNewsReactionViewSet, basename="reactions")
router.register("reactionsUni", UserNewsReactionUnicodeViewSet, basename="reactionsUni")
router.register(
    "toddelreactions", UserToddelReactionViewSet, basename="toddelreactions"
)
router.register(
    "toddelreactionsUni",
    UserToddelReactionUnicodeViewSet,
    basename="toddelreactionsUni",
)
router.register("newsemojis", NewsEmojisViewSet, basename="newsemojis")
router.register("toddelemojis", ToddelEmojisViewSet, basename="toddelemojis")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "emojis/newsemojis/is_allowed/<int:news_id>/",
        NewsEmojisViewSet.as_view({"get": "get_emojis_allowed_status"}),
        name="emojis-allowed",
    ),
]
