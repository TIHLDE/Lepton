from rest_framework import status

import pytest

from app.common.enums import Groups
from app.content.factories.event_factory import EventFactory
from app.content.factories.news_factory import NewsFactory
from app.content.factories.user_factory import UserFactory
from app.emoji.enums import ContentTypes
from app.emoji.factories.reaction_factory import (
    EventReactionFactory,
    NewsReactionFactory,
)
from app.emoji.models.reaction import Reaction
from app.tests.conftest import add_user_to_group_with_name
from app.util.test_utils import get_api_client

API_REACTION_BASE_URL = "/emojis/reactions/"


def _get_reactions_url():
    return API_REACTION_BASE_URL


def _get_reactions_detailed_url(reaction):
    return f"{API_REACTION_BASE_URL}{reaction.reaction_id}/"


def _get_reactions_post_data(content_type, content_id):
    return {
        "emoji": ":smiley:",
        "content_type": content_type,
        "object_id": content_id,
    }


def _get_reactions_put_data():
    return {
        "emoji": ":New_Smiley:",
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("content_type", "object_factory"),
    [
        (ContentTypes.NEWS, NewsFactory),
        (ContentTypes.EVENT, EventFactory),
    ],
)
def test_create_reaction_as_member(member, content_type, object_factory):
    """A member should be able to create a reaction on a supported content type"""
    object_id = object_factory().id
    url = _get_reactions_url()
    client = get_api_client(user=member)
    data = _get_reactions_post_data(content_type, object_id)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("content_type", "object_factory"),
    [
        (ContentTypes.NEWS, NewsFactory),
        (ContentTypes.EVENT, EventFactory),
    ],
)
def test_create_reaction_as_anonymous_user(
    default_client, content_type, object_factory
):
    """An anonymous user should not be able to create a reaction on supported content type"""
    object_id = object_factory().id
    url = _get_reactions_url()

    data = _get_reactions_post_data(content_type, object_id)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("reaction"),
    [
        NewsReactionFactory,
        EventReactionFactory,
    ],
)
def test_update_reaction_as_anonymous_user(default_client, reaction):
    """An anonymous user should not be able to update a reaction on a supported content type"""
    reaction = reaction()
    url = _get_reactions_detailed_url(reaction)

    data = _get_reactions_put_data()
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    reaction.refresh_from_db()
    assert reaction.emoji != data["emoji"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("reaction"),
    [
        NewsReactionFactory,
        EventReactionFactory,
    ],
)
def test_update_own_reaction_as_member(reaction, member):
    """A member should be able to do change their own reaction on a supported content type"""
    reaction = reaction(user=member)
    url = _get_reactions_detailed_url(reaction)
    client = get_api_client(user=member)
    data = _get_reactions_put_data()
    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    reaction.refresh_from_db()
    assert reaction.emoji == data["emoji"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("reaction"),
    [
        NewsReactionFactory,
        EventReactionFactory,
    ],
)
def test_update_not_own_reaction_as_member(reaction, member):
    """A member should not be able to update another user's reaction on a supported content type"""
    reaction = reaction(user=member)
    member = UserFactory()
    add_user_to_group_with_name(member, Groups.TIHLDE)

    url = _get_reactions_detailed_url(reaction)
    client = get_api_client(user=member)
    data = _get_reactions_put_data()
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    reaction.refresh_from_db()
    assert reaction.emoji != data["emoji"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("content_type", "object_factory", "reaction"),
    [
        (ContentTypes.NEWS, NewsFactory, NewsReactionFactory),
        (ContentTypes.EVENT, EventFactory, EventReactionFactory),
    ],
)
def test_create_reaction_twice_as_member(
    reaction, member, content_type, object_factory
):
    """A member should not be able to create more than one reaction on the same supported content type"""
    object_factory()
    reaction = reaction(user=member)
    url = _get_reactions_url()
    client = get_api_client(user=reaction.user)
    data = _get_reactions_post_data(content_type, reaction.object_id)
    data["emoji"] = ":SecondSmiley:"
    response = client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "Du har allerede reagert her"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("reaction"),
    [
        NewsReactionFactory,
        EventReactionFactory,
    ],
)
def test_destroy_own_reaction_as_member(reaction, member):
    """A member should be able to delete their own reaction on a supported content type"""
    reaction = reaction(user=member)
    url = _get_reactions_detailed_url(reaction)
    client = get_api_client(user=reaction.user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert Reaction.objects.filter(user=reaction.user).count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("reaction"),
    [
        NewsReactionFactory,
        EventReactionFactory,
    ],
)
def test_destroy_not_own_reaction_as_member(reaction, member):
    """A member should not be able to delete another user's reaction on a supported content type"""
    reaction = reaction(user=member)
    member = UserFactory()
    add_user_to_group_with_name(member, Groups.TIHLDE)

    url = _get_reactions_detailed_url(reaction)
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Reaction.objects.filter(user=reaction.user).count() == 1
