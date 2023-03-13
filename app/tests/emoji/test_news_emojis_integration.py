from rest_framework import status

import pytest

from app.emoji.factories.custom_emoji_factory import CustomEmojiFactory
from app.util.test_utils import get_api_client

API_EMOJI_BASE_URL = "/emojis/"
API_NEWS_EMOJIS_BASE_URL = f"{API_EMOJI_BASE_URL}newsemojis/"


def _get_news_emojis_url():
    return f"{API_NEWS_EMOJIS_BASE_URL}"


def _get_news_emojis_detailed_url(news_emojis):
    return f"{API_NEWS_EMOJIS_BASE_URL}{news_emojis.id}/"


def _get_news_emojis_post_data(news, emoji):
    return {"news": news.id, "emoji": emoji.id}


def _get_news_emojis_put_data(news_emojis):
    return {
        "news": news_emojis.news.id,
        "emoji": CustomEmojiFactory().id,
    }


@pytest.mark.django_db
def test_that_a_admin_can_create_a_emoji_on_a_news(admin_user, news, emoji):
    """A admin should be able to create a emoji on a news"""

    url = _get_news_emojis_url()
    client = get_api_client(user=admin_user)
    data = _get_news_emojis_post_data(news, emoji)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
