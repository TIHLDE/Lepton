from django.utils import timezone
from rest_framework import status

import pytest

from app.blitzed.factories.drinking_game_factory import DrinkingGameFactory
from app.blitzed.models.drinking_game import DrinkingGame
from app.common.enums import AdminGroup, Groups
from app.util.test_utils import get_api_client

API_DRINKING_GAME_BASE_URL = "/blitzed/drinking_game/"


def _get_drinking_game_url(drinking_game_id=None):
    if drinking_game_id is not None:
        return f"{API_DRINKING_GAME_BASE_URL}{drinking_game_id}/"
    return API_DRINKING_GAME_BASE_URL


@pytest.fixture
def sample_drinking_game():
    return DrinkingGameFactory()


def _get_drinking_game_post_data():
    return {
        "name": "New Drinking Game",
        "description": "This is a new drinking game.",
        "questions": [],
    }


def _get_drinking_game_put_data(drinking_game):
    return {
        "id": drinking_game.id,
        "name": drinking_game.name,
        "description": drinking_game.description,
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_201_CREATED),
        (AdminGroup.INDEX, status.HTTP_201_CREATED),
        (AdminGroup.NOK, status.HTTP_201_CREATED),
        (AdminGroup.PROMO, status.HTTP_201_CREATED),
        (AdminGroup.SOSIALEN, status.HTTP_201_CREATED),
    ],
)
def test_create_drinking_game(member, group_name, expected_status_code):
    """Users in admin groups should be able to create new drinking games."""
    url = _get_drinking_game_url()
    client = get_api_client(user=member, group_name=group_name)
    data = _get_drinking_game_post_data()
    response = client.post(url, data, format="json")

    print(
        f"Group: {group_name}, Expected: {expected_status_code}, Actual: {response.status_code}"
    )

    assert response.status_code == expected_status_code
    assert DrinkingGame.objects.count() == 1
    assert DrinkingGame.objects.get().name == "New Drinking Game"


@pytest.mark.django_db
def test_list_drinking_games(sample_drinking_game, member):
    """A user should be able to retrieve drinking games."""
    url = _get_drinking_game_url()
    client = get_api_client(user=member)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    drinking_games = response.data
    assert len(drinking_games) == 1
    assert drinking_games[0]["name"] == sample_drinking_game.name


@pytest.mark.django_db
def test_list_as_anonymous(default_client):
    """An anonymous user should be able to retrieve drinking games."""
    url = _get_drinking_game_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name",
    list(AdminGroup.all()),
)
def test_update_drinking_game(member, sample_drinking_game, group_name):
    """A member of an admin group user should be able to update a drinking game."""
    url = _get_drinking_game_url(sample_drinking_game.id)
    client = get_api_client(user=member, group_name=group_name)
    data = {
        "name": "Updated Drinking Game",
        "description": "This is an updated drinking game.",
    }
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    sample_drinking_game.refresh_from_db()
    assert sample_drinking_game.name == "Updated Drinking Game"


@pytest.mark.django_db
def test_update_as_anonymous(default_client, drinking_game):
    """An anonymous user should not be able to update a drinking game."""
    data = _get_drinking_game_put_data(drinking_game)
    url = _get_drinking_game_url(drinking_game.id)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_member(member, drinking_game):
    """A member should not be able to update a drinking game."""
    data = _get_drinking_game_put_data(drinking_game)
    url = _get_drinking_game_url(drinking_game.id)
    client = get_api_client(user=member)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name",
    list(AdminGroup.all()),
)
def test_delete_drinking_game_as_admin(member, sample_drinking_game, group_name):
    """Only members of admin groups should be able to delete a drinking game."""
    url = _get_drinking_game_url(sample_drinking_game.id)
    client = get_api_client(user=member, group_name=group_name)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert DrinkingGame.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (Groups.REDAKSJONEN, status.HTTP_403_FORBIDDEN),
        (Groups.JUBKOM, status.HTTP_403_FORBIDDEN),
        (Groups.TIHLDE, status.HTTP_403_FORBIDDEN),
        (Groups.FONDET, status.HTTP_403_FORBIDDEN),
    ],
)
def test_delete_drinking_game_as_non_admin(
    member, sample_drinking_game, group_name, expected_status_code
):
    """Only members of admin groups should be able to delete a drinking game."""
    url = _get_drinking_game_url(sample_drinking_game.id)
    client = get_api_client(user=member, group_name=group_name)
    response = client.delete(url)

    assert response.status_code == expected_status_code
    assert DrinkingGame.objects.count() == 1


@pytest.mark.django_db
def test_delete_drinking_game_as_member(member, sample_drinking_game):
    """Only members of admin groups should be able to delete a drinking game."""
    url = _get_drinking_game_url(sample_drinking_game.id)
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert DrinkingGame.objects.count() == 1


@pytest.mark.django_db
def test_delete_drinking_game_as_non_member(default_client, sample_drinking_game):
    """Only members of admin groups should be able to delete a drinking game."""
    url = _get_drinking_game_url(sample_drinking_game.id)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert DrinkingGame.objects.count() == 1


@pytest.mark.django_db
def test_ordering_of_drinking_games():
    """Drinking games should be ordered by creation."""
    drinking_game1 = DrinkingGame.objects.create(
        name="Game 1", description="Description 1", created_at=timezone.now()
    )
    drinking_game2 = DrinkingGame.objects.create(
        name="Game 2", description="Description 2", created_at=timezone.now()
    )
    drinking_game3 = DrinkingGame.objects.create(
        name="Game 3", description="Description 3", created_at=timezone.now()
    )

    url = _get_drinking_game_url()
    client = get_api_client()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    drinking_games = response.data
    assert len(drinking_games) == 3
    assert drinking_games[0]["name"] == drinking_game3.name
    assert drinking_games[1]["name"] == drinking_game2.name
    assert drinking_games[2]["name"] == drinking_game1.name
