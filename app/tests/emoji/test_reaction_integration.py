from rest_framework import status

import pytest

from app.common.enums import Groups
from app.content.factories.user_factory import UserFactory
from app.emoji.models.reaction import Reaction
from app.tests.conftest import add_user_to_group_with_name
from app.util.test_utils import get_api_client

API_REACTION_BASE_URL = "/emojis/reactions/"


def _get_reactions_url():
    return API_REACTION_BASE_URL


def _get_reactions_detailed_url(reaction):
    return f"{API_REACTION_BASE_URL}{reaction.reaction_id}/"


def _get_reactions_post_data(user, news_id):
    return {
        "user": user.user_id,
        "emoji": ":smiley:",
        "content_type": "news",
        "object_id": news_id,
    }


def _get_reactions_put_data():
    return {
        "emoji": ":Newsmiley:",
    }


@pytest.mark.django_db
def test_that_a_member_can_react_on_news(member, news):
    """A member should be able to do leave a reaction on a news page"""
    url = _get_reactions_url()
    client = get_api_client(user=member)
    data = _get_reactions_post_data(member, news.id)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_member_can_change_reaction_on_news(news_reaction):
    """A member should be able to do change their reaction on a news page"""
    url = _get_reactions_detailed_url(news_reaction)
    client = get_api_client(user=news_reaction.user)
    data = _get_reactions_put_data()
    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    news_reaction.refresh_from_db()
    assert news_reaction.emoji == data["emoji"]


@pytest.mark.django_db
def test_that_a_member_cannot_change_another_users_reaction_on_news(news_reaction):
    """A member should not be able to change another user's reaction on a news page"""
    malicious_user = UserFactory()
    add_user_to_group_with_name(malicious_user, Groups.TIHLDE)
    assert malicious_user.user_id != news_reaction.user.user_id

    url = _get_reactions_detailed_url(news_reaction)
    client = get_api_client(user=malicious_user)
    data = _get_reactions_put_data()
    response = client.put(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    news_reaction.refresh_from_db()
    assert news_reaction.emoji != data["emoji"]


@pytest.mark.django_db
def test_that_a_member_can_not_react_on_news_more_than_once(news_reaction):
    """A member should not be able to leave more than one reaction on the same news page"""
    url = _get_reactions_url()
    client = get_api_client(user=news_reaction.user)
    data = _get_reactions_post_data(news_reaction.user, news_reaction.object_id)
    data["emoji"] = ":Smiley:"
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Reaction.objects.filter(user=news_reaction.user).count() == 1


@pytest.mark.django_db
def test_that_a_member_can_remove_their_reaction_on_a_news(news_reaction):
    """A member should be able to remove their reaction on a news page"""
    url = _get_reactions_detailed_url(news_reaction)
    client = get_api_client(user=news_reaction.user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert Reaction.objects.filter(user=news_reaction.user).count() == 0


@pytest.mark.django_db
def test_that_a_non_member_cannot_react_on_news(user, news, default_client):
    """A non-member should not be able to leave a reaction on a news page"""
    url = _get_reactions_url()
    data = _get_reactions_post_data(user, news.id)
    response = default_client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Reaction.objects.filter(object_id=news.id).count() == 0
