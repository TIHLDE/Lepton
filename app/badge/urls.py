from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.badge.views import (
    BadgeViewSet,
    LeaderboardForBadgeViewSet,
    LeaderboardViewSet,
)

router = routers.DefaultRouter()

router.register("leaderboard", LeaderboardViewSet, basename="leaderboard")
router.register(
    r"(?P<id>[^\.]+)/leaderboard",
    LeaderboardForBadgeViewSet,
    basename="leaderboard-badge",
)
router.register("", BadgeViewSet, basename="badge")

urlpatterns = [
    path("", include(router.urls)),
]
