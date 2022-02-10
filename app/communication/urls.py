from django.conf.urls import include, url
from rest_framework import routers

from app.communication.views import (
    BannerViewSet,
    NotificationViewSet,
    WarningViewSet,
)

router = routers.DefaultRouter()

router.register("banners", BannerViewSet, basename="banner")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("warnings", WarningViewSet, basename="warning")


urlpatterns = [url(r"", include(router.urls))]
