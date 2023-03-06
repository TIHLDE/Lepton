import factory
from factory.django import DjangoModelFactory

from app.content.factories.toddel_factory import ToddelFactory
from app.content.factories.user_factory import UserFactory
from app.emoji.factories.custom_emoji_factory import CustomEmojiFactory
from app.emoji.models.user_toddel_reaction import UserToddelReaction


class UserToddelReactionFactory(DjangoModelFactory):
    class Meta:
        model = UserToddelReaction

    user = factory.SubFactory(UserFactory)
    toddel = factory.SubFactory(ToddelFactory)
    emoji = factory.SubFactory(CustomEmojiFactory)
