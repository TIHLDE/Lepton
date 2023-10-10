from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.blitzed.views.session import SessionViewset

router = routers.DefaultRouter()

router.register("session", SessionViewset, basename="session")

urlpatterns = [
    path("", include(router.urls)),
]
