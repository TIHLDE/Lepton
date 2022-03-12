from django.urls import include, re_path
from rest_framework import routers

from app.communication.views import NotificationViewSet, WarningViewSet

router = routers.DefaultRouter()

router.register("notifications", NotificationViewSet, basename="notification")
router.register("warnings", WarningViewSet, basename="warning")

urlpatterns = [re_path(r"", include(router.urls))]
