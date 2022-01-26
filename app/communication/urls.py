from django.conf.urls import include, url
from rest_framework import routers

from app.communication.views.warning import WarningViewSet

router = routers.DefaultRouter()

router.register("warnings", WarningViewSet, basename="warning")

urlpatterns = [url(r"", include(router.urls))]
