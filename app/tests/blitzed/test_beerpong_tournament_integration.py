from rest_framework import status

import pytest

from app.blitzed.factories.beerpong_tournament_factory import (
    BeerpongTournamentFactory,
)
from app.blitzed.factories.pong_team_factory import PongTeamFactory
from app.blitzed.models.pong_team import PongTeam

API_TOURNAMENT_BASE_URL = "/blitzed/tournament/"


def _get_tournament_url():
    return API_TOURNAMENT_BASE_URL


def _get_detailed_tournament_url(tournament):
    return f"{API_TOURNAMENT_BASE_URL}{tournament.id}/"


@pytest.mark.django_db
def test_that_a_pong_team_is_deleted_if_the_tournament_is_deleted(default_client):
    """A pong team should be deleted if the tournament is deleted"""
    team = PongTeamFactory()
    tournament = BeerpongTournamentFactory.create(teams=[team])

    url = _get_detailed_tournament_url(tournament)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert PongTeam.objects.filter(id=team.id).count() == 0
