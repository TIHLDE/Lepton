from django.urls import include, path
from rest_framework import routers

from app.badge.views import (
    BadgeCategoryViewSet,
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
router.register("categories", BadgeCategoryViewSet, basename="categories")
router.register("", BadgeViewSet, basename="badge")

urlpatterns = [
    path("", include(router.urls)),
]
