from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from app.blitzed.views.beerpong_tournament import BeerpongTournamentViewset
from app.blitzed.views.drinking_game import DrinkingGameViewSet
from app.blitzed.views.pong_match import PongMatchViewset
from app.blitzed.views.pong_result import PongResultViewset
from app.blitzed.views.pong_team import PongTeamViewset
from app.blitzed.views.question import QuestionViewSet
from app.blitzed.views.session import SessionViewset
from app.blitzed.views.user_wasted_level import UserWastedLevelViewset

router = routers.DefaultRouter()

router.register("session", SessionViewset, basename="session")
router.register(
    "user_wasted_level", UserWastedLevelViewset, basename="user_wasted_level"
)
router.register("drinking_game", DrinkingGameViewSet, basename="drinking_game")
router.register("question", QuestionViewSet, basename="question")
router.register("tournament", BeerpongTournamentViewset, basename="tournament")
router.register("match", PongMatchViewset, basename="match")
router.register("result", PongResultViewset, basename="result")
router.register("team", PongTeamViewset, basename="team")

urlpatterns = [
    path("", include(router.urls)),
]