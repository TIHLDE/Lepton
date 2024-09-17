from django.urls import include, path, re_path
from rest_framework import routers

from app.codex.views import CourseViewSet

router = routers.DefaultRouter()

router.register("courses", CourseViewSet)


urlpatterns = [
    re_path(r"", include(router.urls)),
]
