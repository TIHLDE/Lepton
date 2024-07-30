from django.urls import include, path, re_path
from rest_framework import routers

from app.content.views import (
    CategoryViewSet,
    CheatsheetViewSet,
    EventViewSet,
    LogEntryViewSet,
    MinuteViewSet,
    NewsViewSet,
    PageViewSet,
    QRCodeViewSet,
    RegistrationViewSet,
    ShortLinkViewSet,
    StrikeViewSet,
    ToddelViewSet,
    UserBioViewset,
    UserCalendarEvents,
    UserViewSet,
    accept_form,
    upload,
    register_with_feide,
)

router = routers.DefaultRouter()

# Register content viewpoints here
router.register("toddel", ToddelViewSet)
router.register("news", NewsViewSet)
router.register("events", EventViewSet, basename="event")
router.register("categories", CategoryViewSet)
router.register("short-links", ShortLinkViewSet, basename="short-link")
router.register("qr-codes", QRCodeViewSet, basename="qr-code")
router.register("users", UserViewSet, basename="user")
router.register("user-bios", UserBioViewset, basename="user-bio")
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
router.register("log-entries", LogEntryViewSet, basename="log-entries")
router.register("minutes", MinuteViewSet, basename="minutes")

urlpatterns = [
    re_path(r"", include(router.urls)),
    path("accept-form/", accept_form),
    path("upload/", upload),
    path("feide/", register_with_feide),
    re_path(r"users/(?P<user_id>[^/.]+)/events.ics", UserCalendarEvents()),
]
