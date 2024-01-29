from django.urls import include, path, re_path
from rest_framework import routers

from app.content.views import (
    CategoryViewSet,
    CheatsheetViewSet,
    EventViewSet,
    NewsViewSet,
    PageViewSet,
    QRCodeViewSet,
    RegistrationViewSet,
    ShortLinkViewSet,
    StrikeViewSet,
    ToddelViewSet,
    UserCalendarEvents,
    UserViewSet,
    accept_form,
    upload,
    UserBioViewset,
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

urlpatterns = [
    re_path(r"", include(router.urls)),
    path("accept-form/", accept_form),
    path("upload/", upload),
    re_path(r"users/(?P<user_id>[^/.]+)/events.ics", UserCalendarEvents()),
]
