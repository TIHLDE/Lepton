from rest_framework import status

import pytest

from app.blitzed.factories.pong_match_factory import PongMatchFactory
from app.blitzed.factories.pong_result_factory import PongResultFactory
from app.blitzed.factories.pong_team_factory import PongTeamFactory
from app.blitzed.models.pong_result import PongResult

API_RESULT_BASE_URL = "/blitzed/result/"


def _get_result_url():
    return API_RESULT_BASE_URL


def _get_detailed_result_url(result):
    return f"{API_RESULT_BASE_URL}{result.id}/"


def _get_result_post_data(match):
    return {
        "match": match.id,
        "result": "3 - 6",
    }


def _get_result_put_data(result):
    return {
        "result": "6 - 2",
    }


@pytest.mark.django_db
def test_that_a_pong_result_can_be_created(default_client, pong_match):
    """A pong result should be able to be created for a match"""
    url = _get_result_url()
    data = _get_result_post_data(pong_match)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert PongResult.objects.filter(id=response.data["id"]).count() == 1


@pytest.mark.django_db
def test_that_a_pong_result_raises_exception_on_invalid_result(
    default_client, pong_match
):
    """A pong result should raise exception on invalid result"""
    url = _get_result_url()
    data = _get_result_post_data(pong_match)
    data["result"] = "w - l"
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "Noe gikk galt ved lagring av resultat."


@pytest.mark.django_db
def test_that_only_one_pong_result_can_be_created_for_a_match(
    default_client, pong_match
):
    """Only one pong result should be able to be created for a match"""
    PongResultFactory(match=pong_match)
    url = _get_result_url()
    data = _get_result_post_data(pong_match)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert PongResult.objects.filter(match=pong_match).count() == 1


@pytest.mark.django_db
def test_that_a_pong_result_created_with_no_winner_returns_error(
    default_client, pong_match
):
    """A pong result created should return error when score is equal"""
    url = _get_result_url()
    data = _get_result_post_data(pong_match)
    data["result"] = "6 - 6"
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_that_a_pong_result_created_sets_the_correct_winner_of_the_match(
    default_client, pong_match
):
    """A pong result should set the correct winner when created for a match"""
    url = _get_result_url()
    data = _get_result_post_data(pong_match)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    pong_match.refresh_from_db()
    assert (
        PongResult.objects.get(id=response.data["id"]).winner.id == pong_match.team2.id
    )


@pytest.mark.django_db
def test_that_a_pong_result_created_also_updates_the_tournament(
    default_client, beerpong_tournament
):
    """A pong result created should update the tournament aswell"""
    team1 = PongTeamFactory(tournament=beerpong_tournament)
    team2 = PongTeamFactory(tournament=beerpong_tournament)
    team3 = PongTeamFactory(tournament=beerpong_tournament)
    match2 = PongMatchFactory(tournament=beerpong_tournament, team1=team3, team2=None)
    match1 = PongMatchFactory(
        tournament=beerpong_tournament, team1=team1, team2=team2, future_match=match2
    )

    url = _get_result_url()
    data = _get_result_post_data(match1)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert match1.team2.id == response.data["winner"]["id"]
    match2.refresh_from_db()
    assert match2.team2 == team2
    assert PongResult.objects.get(id=response.data["id"]).winner is not None


@pytest.mark.django_db
def test_that_a_pong_result_updated_also_updates_the_tournament(
    default_client, beerpong_tournament
):
    """A pong result updated should update the tournament aswell"""
    team1 = PongTeamFactory(tournament=beerpong_tournament)
    team2 = PongTeamFactory(tournament=beerpong_tournament)
    team3 = PongTeamFactory(tournament=beerpong_tournament)
    match2 = PongMatchFactory(tournament=beerpong_tournament, team1=team3, team2=team2)
    match1 = PongMatchFactory(
        tournament=beerpong_tournament, team1=team1, team2=team2, future_match=match2
    )
    result = PongResultFactory(match=match1, winner=team2, result="0 - 6")
    url = _get_detailed_result_url(result)
    data = _get_result_put_data(result)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    match2.refresh_from_db()
    assert match2.team2.id == team1.id
    result.refresh_from_db()
    assert match1.team1.id == result.winner.id
    assert PongResult.objects.get(id=response.data["id"]).winner is not None


@pytest.mark.django_db
def test_that_a_pong_result_can_be_updated(default_client, pong_match):
    """A pong result should be able to be updated for a match"""
    result = PongResultFactory(match=pong_match)

    url = _get_detailed_result_url(result)
    data = _get_result_put_data(result)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_a_pong_result_can_be_deleted(default_client, pong_match):
    """A pong result should be able to be deleted from a match"""
    result = PongResultFactory(match=pong_match)

    url = _get_detailed_result_url(result)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert PongResult.objects.filter(match=pong_match.id).count() == 0


@pytest.mark.django_db
def test_that_a_pong_result_deleted_updates_a_tournament(
    default_client, beerpong_tournament
):
    """A pong result deleted should update the tournament aswell"""
    team1 = PongTeamFactory(tournament=beerpong_tournament)
    team2 = PongTeamFactory(tournament=beerpong_tournament)
    team3 = PongTeamFactory(tournament=beerpong_tournament)
    match2 = PongMatchFactory(tournament=beerpong_tournament, team1=team3, team2=team2)
    match1 = PongMatchFactory(
        tournament=beerpong_tournament, team1=team1, team2=team2, future_match=match2
    )
    result = PongResultFactory(match=match1, winner=team2, result="0 - 6")

    url = _get_detailed_result_url(result)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert PongResult.objects.filter(match=match1.id).count() == 0
    match2.refresh_from_db()
    assert match2.team2 is None
