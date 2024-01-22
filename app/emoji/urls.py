from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.emoji.views.reaction import ReactionViewSet

router = routers.DefaultRouter()

router.register("reactions", ReactionViewSet, basename="reactions")

urlpatterns = [
    path("", include(router.urls)),
]
