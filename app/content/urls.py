from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers

from rest_framework_swagger.views import get_swagger_view

from .views import (
    CategoryViewSet,
    CheatsheetViewSet,
    EventViewSet,
    JobPostViewSet,
    NewsViewSet,
    NotificationViewSet,
    UserChallengeViewSet,
    UserEventViewSet,
    UserViewSet,
    WarningViewSet,
    accept_form,
)

router = routers.DefaultRouter()

# Register content viewpoints here
router.register("news", NewsViewSet)
router.register("events", EventViewSet, basename="event")
router.register("warning", WarningViewSet, basename="warning")
router.register("category", CategoryViewSet)
router.register("jobpost", JobPostViewSet, basename="jobpost")
router.register("user", UserViewSet, basename="user")
router.register(
    r"events/(?P<event_id>\d+)/users", UserEventViewSet, basename="user_event"
)
router.register("notification", NotificationViewSet, basename="notification")
router.register(
    r"cheatsheet/study/(?P<study>[^\.]+)/grade/(?P<grade>[^\.]+)/file",
    CheatsheetViewSet,
    basename="cheatsheet_list",
)
router.register("challenge", UserChallengeViewSet, basename="challenge")

# Swagger
schema_view = get_swagger_view(title="TIHLDE API")


urlpatterns = [
    url(r"docs", schema_view),
    url(r"", include(router.urls)),
    path("accept-form/", accept_form),
]
