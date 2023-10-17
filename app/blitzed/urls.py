from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.blitzed.views.anonymous_user import AnonymousUserViewset
from app.blitzed.views.beerpong_tournamnet import BeerpongTournamentViewset
from app.blitzed.views.pong_match import PongMatchViewset
from app.blitzed.views.pong_result import PongResultViewset
from app.blitzed.views.pong_team import PongTeamViewset
from app.blitzed.views.session import SessionViewset

router = routers.DefaultRouter()

router.register("session", SessionViewset, basename="session")
router.register("tournament", BeerpongTournamentViewset, basename="tournament")
router.register("match", PongMatchViewset, basename="match")
router.register("result", PongResultViewset, basename="result")
router.register("team", PongTeamViewset, basename="team")
router.register("anonymous", AnonymousUserViewset, basename="anonymous")

urlpatterns = [
    path("", include(router.urls)),
]
