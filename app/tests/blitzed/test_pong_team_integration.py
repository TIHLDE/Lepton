from rest_framework import status

import pytest

from app.blitzed.factories.anonymous_user_factory import AnonymousUserFactory
from app.blitzed.factories.pong_team_factory import PongTeamFactory
from app.blitzed.models.anonymous_user import AnonymousUser
from app.content.factories.user_factory import UserFactory

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
        "tournament": beerpong_tournament.id,
    }


def _get_team_put_data(team, beerpong_tournament):
    members = list(team.members.all())
    members.append(UserFactory())
    anonymous_members = list(team.anonymous_members.all())
    anonymous_members.append(AnonymousUserFactory())
    return {
        "team_name": "Margarita Mavericks",
        "members": [member.user_id for member in members],
        "anonymous_members": [
            {"id": member.id, "name": member.name} for member in anonymous_members
        ],
        "tournament": beerpong_tournament.id,
    }


def _get_user_list():
    return [UserFactory().user_id, UserFactory().user_id]


def _get_anonymous_user_list():
    return [{"name": "John Doe"}, {"name": "Jane Doe"}]


@pytest.mark.django_db
def test_that_a_pong_team_can_be_created_with_users_and_anonymous_users(
    default_client, beerpong_tournament
):
    """A pong team should be able to be created with bouth users and anonymous users for a tournament"""
    anonymous_members = [{"name": "John Doe"}, {"name": "Jane Doe"}]
    members = [UserFactory().user_id]

    url = _get_team_url()
    data = _get_team_post_data(beerpong_tournament, members, anonymous_members)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_pong_team_can_be_created_with_new_anonymous_users(
    default_client, beerpong_tournament
):
    """A pong team should be able to be created with new anonymous users for a tournament"""

    url = _get_team_url()
    data = _get_team_post_data(beerpong_tournament, [], [])
    data["anonymous_members"] = [{"name": "John Doe"}, {"name": "Jane Doe"}]
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_pong_team_can_be_updated_with_new_anonymous_users(
    default_client, beerpong_tournament
):
    """A pong team should be able to be updated for a tournament with new anonymous users"""
    team = PongTeamFactory(tournament=beerpong_tournament)

    url = _get_detailed_team_url(team)
    data = _get_team_put_data(team, beerpong_tournament)
    data["anonymous_members"] = [{"name": "John Doe"}, {"name": "Jane Doe"}]
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_a_pong_team_can_not_be_created_without_a_tournament(default_client):
    """A pong team should not be able to be created without a tournament"""
    url = _get_team_url()
    data = {
        "team_name": "Margarita Mavericks",
        "members": [],
        "anonymous_members": [],
    }
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_that_a_pong_team_can_be_created_with_only_users(
    default_client, beerpong_tournament
):
    """A pong team should be able to be created with only users for a tournament"""
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
    """A pong team should be able to be created with only anonymous users for a tournament"""
    anonymous_members = _get_anonymous_user_list()
    members = []

    url = _get_team_url()
    data = _get_team_post_data(beerpong_tournament, members, anonymous_members)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_pong_team_can_be_updated(default_client, beerpong_tournament):
    """A pong team should be able to be updated for a tournament"""
    team = PongTeamFactory(tournament=beerpong_tournament)

    url = _get_detailed_team_url(team)
    data = _get_team_put_data(team, beerpong_tournament)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_a_pong_team_can_be_deleted(default_client, beerpong_tournament):
    """A pong team should be able to be deleted from a tournament"""
    team1 = PongTeamFactory(tournament=beerpong_tournament)
    PongTeamFactory(tournament=beerpong_tournament)
    old_count = beerpong_tournament.teams.count()

    url = _get_detailed_team_url(team1)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    beerpong_tournament.refresh_from_db()
    assert beerpong_tournament.teams.count() < old_count


@pytest.mark.django_db
def test_that_when_a_pong_team_is_deleted_anonymous_users_also_gets_deleted(
    default_client, anonymous_user
):
    """Anonymous users should be deleted when a pong team is deleted"""
    team = PongTeamFactory.create(anonymous_members=[anonymous_user])

    url = _get_detailed_team_url(team)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert AnonymousUser.objects.filter(id=anonymous_user.id).count() == 0
