from django.urls import include, path, re_path
from rest_framework import routers

from app.wrapped.views.wrapped import WrappedStatsView

router = routers.DefaultRouter()

router.register(r"stats", WrappedStatsView, basename="statistics")

urlpatterns = [
    re_path(r"", include(router.urls)),
]
