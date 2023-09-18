from rest_framework import status

import pytest

from app.content.factories.toddel_factory import ToddelFactory
from app.content.factories.user_factory import UserFactory
from app.emoji.factories.custom_emoji_factory import CustomEmojiFactory
from app.emoji.factories.toddel_emojis_factory import ToddelEmojisFactory
from app.emoji.factories.user_toddel_reaction_factory import (
    UserToddelReactionFactory,
)
from app.util.test_utils import get_api_client

API_EMOJI_BASE_URL = "/emojis/"


def _get_reactions_url():
    return f"{API_EMOJI_BASE_URL}toddelreactions/"


def _get_reactions_detailed_url(reaction):
    return f"{_get_reactions_url()}{reaction.id}/"


def _get_detailed_reactions_url(reaction):
    return f"{_get_reactions_url()}{reaction.id}/"


def _get_reactions_post_data(user, toddel, emoji):
    return {"user": user.user_id, "toddel": toddel.edition, "emoji": emoji.id}


def _get_reactions_put_data(reaction):
    return {
        "user": reaction.user.user_id,
        "toddel": reaction.toddel.edition,
        "emoji": CustomEmojiFactory().id,
    }


def _get_reactions_put_data_with_emoji(reaction):
    return {
        "user": reaction.user.user_id,
        "toddel": reaction.toddel.edition,
        "emoji": CustomEmojiFactory().id,
    }


@pytest.mark.django_db
def test_that_a_member_can_react_on_toddel(member):
    """A member should be able to do leave a reaction on a toddel"""

    emoji = CustomEmojiFactory()
    toddel = ToddelFactory()
    ToddelEmojisFactory(toddel=toddel, emojis_allowed=True)

    url = _get_reactions_url()
    client = get_api_client(user=member)
    data = _get_reactions_post_data(member, toddel, emoji)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_non_member_cannot_react_on_toddel(user):
    """A non-member should not be able to leave a reaction on a toddel"""

    emoji = CustomEmojiFactory()
    toddel = ToddelFactory()
    ToddelEmojisFactory(toddel=toddel, emojis_allowed=True)

    url = _get_reactions_url()
    client = get_api_client(user)
    data = _get_reactions_post_data(user, toddel, emoji)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_that_a_member_can_change_reaction(member):
    """A member should be able to change their reaction on a toddel"""

    reaction = UserToddelReactionFactory(user=member)
    ToddelEmojisFactory(toddel=reaction.toddel, emojis_allowed=True)

    client = get_api_client(user=member)
    data = _get_reactions_put_data_with_emoji(reaction)
    url = _get_reactions_detailed_url(reaction)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_a_member_can_not_post_a_reaction_for_another_member(member):
    """A member should not be able to post a reaction for another member on a toddel"""

    emoji = CustomEmojiFactory()
    toddel = ToddelFactory()
    ToddelEmojisFactory(toddel=toddel, emojis_allowed=True)

    url = _get_reactions_url()
    client = get_api_client(user=member)
    data = _get_reactions_post_data(UserFactory(), toddel, emoji)
    response = client.put(url, data)

    assert member != data["user"]
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_that_a_member_can_not_post_multiple_reactions_on_the_same_toddel(member):
    """A member should not be able to post multiple reactions on the same toddel"""
    toddel = ToddelFactory()
    ToddelEmojisFactory(toddel=toddel, emojis_allowed=True)
    url = _get_reactions_url()
    client = get_api_client(user=member)
    reaction = UserToddelReactionFactory(user=member, toddel=toddel)
    data = _get_reactions_put_data(reaction)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.django_db
def test_that_a_member_can_delete_their_reaction(member):
    """A member should be able to remove their reaction from a toddel"""

    url = _get_detailed_reactions_url(UserToddelReactionFactory(user=member))
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_non_member_can_not_see_the_reactions_on_a_toddel(default_client):
    """A non member should not be able to view reactions on a toddel"""

    url = _get_reactions_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
