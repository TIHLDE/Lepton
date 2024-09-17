from django.urls import include, re_path
from rest_framework import routers

from app.codex.views import CourseViewSet, RegistrationViewSet

router = routers.DefaultRouter()

router.register("courses", CourseViewSet)
router.register(
    r"courses/(?P<course_id>\d+)/registrations",
    RegistrationViewSet,
    basename="registration",
)


urlpatterns = [
    re_path(r"", include(router.urls)),
]
