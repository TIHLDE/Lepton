import factory
from factory.django import DjangoModelFactory

from app.content.factories.news_factory import NewsFactory
from app.content.factories.user_factory import UserFactory
from app.emoji.factories.custom_emoji_factory import CustomEmojiFactory
from app.emoji.models.user_news_reaction import UserNewsReaction


class UserNewsReactionFactory(DjangoModelFactory):
    class Meta:
        model = UserNewsReaction

    user = factory.SubFactory(UserFactory)
    news = factory.SubFactory(NewsFactory)
    emoji = factory.SubFactory(CustomEmojiFactory)