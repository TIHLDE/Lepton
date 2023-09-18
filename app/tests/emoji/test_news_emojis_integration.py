from rest_framework import status

import pytest

from app.emoji.factories.news_emojis_factory import NewsEmojisFactory
from app.util.test_utils import get_api_client

API_EMOJI_BASE_URL = "/emojis/"
API_NEWS_EMOJIS_BASE_URL = f"{API_EMOJI_BASE_URL}newsemojis/"


def _get_news_emojis_url():
    return f"{API_NEWS_EMOJIS_BASE_URL}"


def _get_news_emojis_detailed_url(news_emojis):
    return f"{API_NEWS_EMOJIS_BASE_URL}{news_emojis.id}/"


def _get_news_emojis_post_data(news, emojis_allowed):
    return {"news": news.id, "emojis_allowed": emojis_allowed}


def _get_news_emojis_put_data(news_emojis):
    return {
        "news": news_emojis.news.id,
        "emojis_allowed": True,
    }


@pytest.mark.django_db
def test_that_a_admin_can_allow_emojis_on_a_news(admin_user, news):
    """A admin should be able to allow emojis on a news"""

    url = _get_news_emojis_url()
    client = get_api_client(user=admin_user)
    data = _get_news_emojis_post_data(news, True)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_member_cannot_allow_emojis_on_a_news(member, news):
    """A member should not be able to create an emoji on a news"""

    url = _get_news_emojis_url()
    client = get_api_client(user=member)
    data = _get_news_emojis_post_data(news, True)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_that_a_nonmember_cannot_allow_emojis_on_a_news(user, news):
    """A nonmember should not be able to allow emojis on a news"""
    url = _get_news_emojis_url()
    client = get_api_client(user)
    data = _get_news_emojis_post_data(news, True)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_that_an_admin_can_change_emojis_allowence_on_a_news(admin_user, news_emojis):
    """An admin should be able to change the emojis allowence on a news"""

    url = _get_news_emojis_detailed_url(news_emojis)
    client = get_api_client(user=admin_user)
    data = _get_news_emojis_put_data(news_emojis)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_an_admin_can_delete_emojis_on_a_news(admin_user):
    """An admin should be able to delete emoji allowence on a news"""

    url = _get_news_emojis_detailed_url(NewsEmojisFactory())
    client = get_api_client(user=admin_user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_an_non_admin_can_not_delete_emojis_allowence_on_a_news(member):
    """A member should not be able to delete emojis allowence on a news"""

    url = _get_news_emojis_detailed_url(NewsEmojisFactory())
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
