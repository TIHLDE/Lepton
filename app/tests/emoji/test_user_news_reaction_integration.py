from rest_framework import status

import pytest

from app.content.factories.user_factory import UserFactory
from app.emoji.factories.custom_emoji_factory import CustomEmojiFactory
from app.emoji.factories.user_news_reaction_factory import (
    UserNewsReactionFactory,
)
from app.util.test_utils import get_api_client

API_EMOJI_BASE_URL = "/emojis/"
API_REACTION_BASE_URL = f"{API_EMOJI_BASE_URL}reactions/"


def _get_reactions_url():
    return f"{API_REACTION_BASE_URL}"


def _get_reactions_detailed_url(reaction):
    return f"{API_REACTION_BASE_URL}{reaction.id}/"


def _get_reactions_post_data(user, news, emoji):
    return {"user": user.user_id, "news": news.id, "emoji": emoji.id}


def _get_reactions_put_data(reaction):
    return {
        "user": reaction.user.user_id,
        "news": reaction.news.id,
        "emoji": CustomEmojiFactory().id,
    }


@pytest.mark.django_db
def test_that_a_member_can_react_on_news(member, news, emoji):
    """A member should be able to do leave a reaction on a news page"""

    url = _get_reactions_url()
    client = get_api_client(user=member)
    data = _get_reactions_post_data(member, news, emoji)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_non_member_cannot_react_on_news(user, news, emoji):
    """A non-member should not be able to leave a reaction on a news page"""
    url = _get_reactions_url()
    client = get_api_client(user)
    data = _get_reactions_post_data(user, news, emoji)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_that_a_member_can_change_reaction(member, reaction):
    """A member should be able to change their reaction on a news page"""

    client = get_api_client(user=member)
    data = _get_reactions_put_data(reaction)
    url = _get_reactions_detailed_url(reaction)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_a_member_can_delete_their_reaction(member):
    """A member should be able to remove their reaction from a news page"""

    client = get_api_client(user=member)
    url = _get_reactions_detailed_url(UserNewsReactionFactory())
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_a_member_can_not_post_multiple_reactions_on_the_same_news(member):
    """A member should not be able to post multiple reactions on the same news page"""

    url = _get_reactions_url()
    client = get_api_client(user=member)
    reaction = UserNewsReactionFactory(user=member)
    data = _get_reactions_put_data(reaction)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.django_db
def test_that_a_member_can_not_post_a_reaction_for_another_member(member, news, emoji):
    """A member should not be able to post a reaction for another member on a news page"""

    url = _get_reactions_url()
    client = get_api_client(user=member)
    data = _get_reactions_post_data(UserFactory(), news, emoji)
    response = client.put(url, data)

    assert member != data["user"]
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_that_a_non_member_can_view_reaction_on_news(user):
    """A member should not be able to post a reaction for another member on a news page"""

    url = _get_reactions_url()
    client = get_api_client(user)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
