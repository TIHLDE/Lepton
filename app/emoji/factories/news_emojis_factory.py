import factory
from factory.django import DjangoModelFactory

from app.content.factories.news_factory import NewsFactory
from app.emoji.factories.custom_emoji_factory import CustomEmojiFactory
from app.emoji.models.news_emojis import NewsEmojis


class NewsEmojisFactory(DjangoModelFactory):
    class Meta:
        model = NewsEmojis

    news = factory.SubFactory(NewsFactory)
    emoji = factory.SubFactory(CustomEmojiFactory)
