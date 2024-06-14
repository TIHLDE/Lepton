from rest_framework import status

import pytest

from app.blitzed.factories.pong_match_factory import PongMatchFactory
from app.blitzed.factories.pong_team_factory import PongTeamFactory

API_MATCH_BASE_URL = "/blitzed/match/"


def _get_match_url():
    return API_MATCH_BASE_URL


def _get_detailed_match_url(match):
    return f"{API_MATCH_BASE_URL}{match.id}/"


def _get_match_post_data(tournament, team1, team2, future_match):
    if future_match:
        return {
            "team1": team1.id,
            "team2": team2.id,
            "future_match": future_match.id,
            "tournament": tournament.id,
            "round": "1",
        }
    return {
        "team1": team1.id,
        "team2": team2.id,
        "future_match": None,
        "tournament": tournament.id,
        "round": "1",
    }


def _get_match_put_data(match, tournament):
    return {
        "team1": PongTeamFactory(tournament=tournament).id,
        "team2": PongTeamFactory(tournament=tournament).id,
        "future_match": PongMatchFactory(tournament=tournament).id,
        "tournament": tournament.id,
        "round": "1",
    }


@pytest.mark.django_db
def test_that_a_pong_match_can_be_created_without_a_future_match(
    default_client, beerpong_tournament
):
    """A pong match should be able to be created for a tournament without a future match"""
    team1 = PongTeamFactory(tournament=beerpong_tournament)
    team2 = PongTeamFactory(tournament=beerpong_tournament)

    url = _get_match_url()
    data = _get_match_post_data(beerpong_tournament, team1, team2, None)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_pong_match_can_be_created_with_a_future_match(
    default_client, beerpong_tournament
):
    """A pong match should be able to be created for a tournament with a future match"""
    team1 = PongTeamFactory(tournament=beerpong_tournament)
    team2 = PongTeamFactory(tournament=beerpong_tournament)
    future_match = PongMatchFactory(tournament=beerpong_tournament)

    url = _get_match_url()
    data = _get_match_post_data(beerpong_tournament, team1, team2, future_match)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_pong_match_can_be_updated(default_client, beerpong_tournament):
    """A pong match should be able to be updated for a tournament"""
    match = PongMatchFactory(tournament=beerpong_tournament)

    url = _get_detailed_match_url(match)
    data = _get_match_put_data(match, beerpong_tournament)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_a_pong_match_can_be_deleted(default_client, beerpong_tournament):
    """A pong match should be able to be deleted from a tournament"""
    match = PongMatchFactory(tournament=beerpong_tournament)
    old_match_count = beerpong_tournament.matches.count()

    url = _get_detailed_match_url(match)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    beerpong_tournament.refresh_from_db()
    assert beerpong_tournament.matches.count() < old_match_count
