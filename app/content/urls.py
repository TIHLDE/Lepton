from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    CheatsheetViewSet,
    EventViewSet,
    JobPostViewSet,
    NewsViewSet,
    NotificationViewSet,
    PageViewSet,
    RegistrationViewSet,
    UserBadgeViewSet,
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
    r"events/(?P<event_id>\d+)/users", RegistrationViewSet, basename="registration"
)
router.register("notification", NotificationViewSet, basename="notification")
router.register(
    r"cheatsheet/(?P<study>[^\.]+)/(?P<grade>[^\.]+)/files",
    CheatsheetViewSet,
    basename="cheatsheet_list",
)
router.register("badge", UserBadgeViewSet, basename="badge")
router.register("page", PageViewSet)

urlpatterns = [
    url(r"", include(router.urls)),
    path("accept-form/", accept_form),
]
