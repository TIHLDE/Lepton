from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers

from app.content.views import (
    CategoryViewSet,
    CheatsheetViewSet,
    EventViewSet,
    NewsViewSet,
    PageViewSet,
    RegistrationViewSet,
    ShortLinkViewSet,
    StrikeViewSet,
    UserCalendarEvents,
    UserViewSet,
    accept_form,
    gdpr,
    upload,
)

router = routers.DefaultRouter()

# Register content viewpoints here
router.register("news", NewsViewSet)
router.register("events", EventViewSet, basename="event")
router.register("categories", CategoryViewSet)
router.register("short-links", ShortLinkViewSet, basename="short-link")
router.register("users", UserViewSet, basename="user")
router.register(
    r"events/(?P<event_id>\d+)/registrations",
    RegistrationViewSet,
    basename="registration",
)
router.register(
    r"cheatsheets/(?P<study>[^\.]+)/(?P<grade>[^\.]+)/files",
    CheatsheetViewSet,
    basename="cheatsheet_list",
)
router.register("pages", PageViewSet)
router.register("strikes", StrikeViewSet, basename="strikes")

urlpatterns = [
    url(r"", include(router.urls)),
    path("accept-form/", accept_form),
    path("upload/", upload),
    path("gdpr/", gdpr),
    url(r"users/(?P<user_id>[^/.]+)/events.ics", UserCalendarEvents()),
]
