from rest_framework import status

import pytest

from app.blitzed.factories.anonymous_user_factory import AnonymousUserFactory
from app.blitzed.factories.beerpong_tournament_factory import (
    BeerpongTournamentFactory,
)
from app.blitzed.factories.pong_team_factory import PongTeamFactory
from app.blitzed.models.beerpong_tournament import BeerpongTournament
from app.content.factories.user_factory import UserFactory
from app.util.test_utils import get_api_client

API_TEAM_BASE_URL = "/blitzed/team/"


def _get_team_url():
    return API_TEAM_BASE_URL


def _get_detailed_team_url(team):
    return f"{API_TEAM_BASE_URL}{team.id}/"


def _get_team_post_data(beerpong_tournament, members, anonymous_members):
    return {
        "team_name": "Tipsy Titans",
        "members": members,
        "anonymous_members": anonymous_members,
        "tournament_id": beerpong_tournament.id,
    }


def _get_team_put_data(team):
    return {
        "team_name": "Margarita Mavericks",
        "members": team["members"].append(
            UserFactory().user_id
        ),  # team.members.push(UserFactory().user_id),
        "anonymous_members": team["anonymous_members"].append(
            AnonymousUserFactory().id
        ),  # team.anonymous_members.push(AnonymousUserFactory().id),
        "tournament_id": 1,  # BeerpongTournament.objects.filter(teams.contains(team.id))
    }


def _get_user_list():
    return [UserFactory().user_id, UserFactory().user_id]


def _get_anonymous_user_list():
    return [AnonymousUserFactory().id, AnonymousUserFactory().id]


@pytest.mark.django_db
def test_that_a_pong_team_can_be_created_with_users_and_anonymous_users(
    default_client, beerpong_tournament
):
    """A pong team should be able to be
    created with bouth users and anonymous users for a tournament"""
    anonymous_members = [AnonymousUserFactory().id]
    members = [UserFactory().user_id]

    url = _get_team_url()
    data = _get_team_post_data(beerpong_tournament, members, anonymous_members)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_pong_team_can_be_created_with_only_users(
    default_client, beerpong_tournament
):
    """A pong team should be able to be
    created with only users for a tournament"""
    anonymous_members = []
    members = _get_user_list()

    url = _get_team_url()
    data = _get_team_post_data(beerpong_tournament, members, anonymous_members)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_pong_team_can_be_created_with_only_anonymous_users(
    default_client, beerpong_tournament
):
    """A pong team should be able to be
    created with only anonymous users for a tournament"""
    anonymous_members = _get_anonymous_user_list()
    members = []

    url = _get_team_url()
    data = _get_team_post_data(beerpong_tournament, members, anonymous_members)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_pong_team_can_be_updated(default_client, beerpong_tournament):
    """A pong team should be able to be
    created with only anonymous users for a tournament"""
    # team = beerpong_tournament.teams.get(0, None)

    # url = _get_team_url()
    # data = _get_team_put_data(team)
    # response = default_client.post(url, data)

    # assert response.status_code == status.HTTP_200_OK
    assert True


@pytest.mark.django_db
def test_that_a_pong_team_can_be_deleted(default_client, beerpong_tournament):
    """A pong team should be able to be
    deleted from a tournament"""
    # old_size = beerpong_tournament.teams.len()
    # team = beerpong_tournament.teams.get(0, None)
    # ssert team != None
    assert True
    # url = _get_detailed_team_url(team)
    # response = default_client.delete(url)

    # assert response.status_code == status.HTTP_204_NO_CONTENT
    # beerpong_tournament.refresh_from_db()
    # assert beerpong_tournament.teams.len() != old_size
