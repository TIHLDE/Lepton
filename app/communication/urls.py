from django.urls import include, re_path
from rest_framework import routers

from app.communication.views import (
    BannerViewSet,
    NotificationViewSet,
    UserNotificationSettingViewSet,
    WarningViewSet,
)

router = routers.DefaultRouter()

router.register("banners", BannerViewSet, basename="banner")
router.register("notifications", NotificationViewSet, basename="notification")
router.register(
    "notification-settings",
    UserNotificationSettingViewSet,
    basename="notification-setting",
)
router.register("warnings", WarningViewSet, basename="warning")


urlpatterns = [re_path(r"", include(router.urls))]
