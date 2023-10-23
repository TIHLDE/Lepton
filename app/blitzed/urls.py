from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.blitzed.views.drinking_game import DrinkingGameViewSet
from app.blitzed.views.session import SessionViewset

router = routers.DefaultRouter()

router.register("session", SessionViewset, basename="session")
router.register("drinking_game", DrinkingGameViewSet, basename="drinking_game")

urlpatterns = [
    path("", include(router.urls)),
]
