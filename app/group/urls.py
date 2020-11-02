from django.conf.urls import include, url
from rest_framework import routers

from app.group.views import GroupViewSet

router = routers.DefaultRouter()
router.register("group", GroupViewSet, basename="group")

# Register group viewpoints here
urlpatterns = [url(r"", include(router.urls))]
