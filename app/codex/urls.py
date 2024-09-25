from django.urls import include, re_path
from rest_framework import routers

from app.codex.views import CodexEventViewSet, RegistrationViewSet

router = routers.DefaultRouter()

router.register("events", CodexEventViewSet)
router.register(
    r"events/(?P<event_id>\d+)/registrations",
    RegistrationViewSet,
    basename="registration",
)


urlpatterns = [
    re_path(r"", include(router.urls)),
]
