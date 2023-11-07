from rest_framework import status

import pytest

from app.blitzed.factories.pong_match_factory import PongMatchFactory
from app.blitzed.factories.pong_team_factory import PongTeamFactory
from app.blitzed.models.pong_match import PongMatch
from app.blitzed.models.pong_team import PongTeam

API_TOURNAMENT_BASE_URL = "/blitzed/tournament/"


def _get_tournament_url():
    return API_TOURNAMENT_BASE_URL


def _get_tournament_generate_url(tournament):
    return f"{API_TOURNAMENT_BASE_URL}{tournament.id}/generate/"


def _get_tournament_by_name_url(tournament):
    return f"{API_TOURNAMENT_BASE_URL}?name={tournament.name}"


def _get_detailed_tournament_url(tournament):
    return f"{API_TOURNAMENT_BASE_URL}{tournament.id}/"


def _get_tournament_post_data():
    return {
        "name": "Beerolympics",
    }


def _get_tournament_put_data():
    return {
        "name": "Beerolympics-2",
    }


@pytest.mark.django_db
def test_that_a_tournament_can_be_created(default_client):
    """A tournament should be able to be created"""
    url = _get_tournament_url()
    data = _get_tournament_post_data()
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_tournament_can_be_retrieved(default_client, beerpong_tournament):
    """A tournament should be able to be retrieved by id"""
    url = _get_detailed_tournament_url(beerpong_tournament)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == beerpong_tournament.id


@pytest.mark.django_db
def test_that_a_tournament_can_be_updated(default_client, beerpong_tournament):
    """A tournament should be able to be updated"""
    url = _get_detailed_tournament_url(beerpong_tournament)
    data = _get_tournament_put_data()
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_a_tournament_can_be_generated(default_client, beerpong_tournament):
    """A tournament should be able to generate mathces with the given teams"""
    PongTeamFactory(tournament=beerpong_tournament)
    PongTeamFactory(tournament=beerpong_tournament)
    PongTeamFactory(tournament=beerpong_tournament)

    url = _get_tournament_generate_url(beerpong_tournament)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert PongMatch.objects.filter(tournament=beerpong_tournament).count() == 2
    match1 = PongMatch.objects.filter(tournament=beerpong_tournament)[0]
    assert match1.team1 is not None and match1.team2 is not None
    match2 = PongMatch.objects.filter(tournament=beerpong_tournament)[1]
    assert match2.team1 is not None and match2.team2 is None


@pytest.mark.django_db
def test_that_a_tournament_can_be_retrieved_by_name(
    default_client, beerpong_tournament
):
    """A tournament should be able to be retrieved by name"""
    url = _get_tournament_by_name_url(beerpong_tournament)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["id"] == beerpong_tournament.id


@pytest.mark.django_db
def test_that_a_tournament_updates_its_self_when_new_tournament_is_generated(
    default_client, beerpong_tournament
):
    """A tournament should just update it's matches when geenerating tournament if the tournament already have matches"""
    team1 = PongTeamFactory(tournament=beerpong_tournament)
    team2 = PongTeamFactory(tournament=beerpong_tournament)
    team3 = PongTeamFactory(tournament=beerpong_tournament)
    match2 = PongMatchFactory(tournament=beerpong_tournament, team1=team3, team2=None)
    PongMatchFactory(
        tournament=beerpong_tournament, team1=team1, team2=team2, future_match=match2
    )

    assert PongMatch.objects.filter(tournament=beerpong_tournament).count() == 2

    url = _get_tournament_generate_url(beerpong_tournament)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert PongMatch.objects.filter(tournament=beerpong_tournament).count() == 2


@pytest.mark.django_db
def test_that_a_tournament_can_be_deleted(default_client, beerpong_tournament):
    """A tournament should be able to be deleted"""
    url = _get_detailed_tournament_url(beerpong_tournament)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_200_OK


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
