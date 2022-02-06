from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.badge.views import UserBadgeViewSet

router = routers.DefaultRouter()

router.register("", UserBadgeViewSet, basename="badge")

urlpatterns = [
    path("", include(router.urls))
]
