from django.conf.urls import include, url
from rest_framework import routers

from app.communication.views import NotificationViewSet, UserNotificationSettingViewSet, WarningViewSet

router = routers.DefaultRouter()

router.register("notifications", NotificationViewSet, basename="notification")
router.register("notification-settings", UserNotificationSettingViewSet, basename="notification-setting")
router.register("warnings", WarningViewSet, basename="warning")

urlpatterns = [url(r"", include(router.urls))]
