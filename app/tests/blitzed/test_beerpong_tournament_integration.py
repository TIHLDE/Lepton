from rest_framework import status

import pytest

from app.blitzed.factories.pong_match_factory import PongMatchFactory
from app.blitzed.factories.pong_team_factory import PongTeamFactory
from app.blitzed.models.pong_match import PongMatch
from app.blitzed.models.pong_team import PongTeam

API_TOURNAMENT_BASE_URL = "/blitzed/tournament/"


def _get_tournament_url():
    return API_TOURNAMENT_BASE_URL


def _get_detailed_tournament_url(tournament):
    return f"{API_TOURNAMENT_BASE_URL}{tournament.id}/"


@pytest.mark.django_db
def test_that_a_pong_team_is_deleted_if_the_tournament_is_deleted(
    default_client, beerpong_tournament
):
    """A pong team should be deleted if the tournament is deleted"""
    team = PongTeamFactory(tournament=beerpong_tournament)

    url = _get_detailed_tournament_url(beerpong_tournament)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert PongTeam.objects.filter(id=team.id).count() == 0


@pytest.mark.django_db
def test_that_a_pong_match_is_deleted_if_the_tournament_is_deleted(
    default_client, beerpong_tournament
):
    """A pong match should be deleted if the tournament is deleted"""
    match = PongMatchFactory(tournament=beerpong_tournament)

    url = _get_detailed_tournament_url(beerpong_tournament)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert PongMatch.objects.filter(id=match.id).count() == 0
