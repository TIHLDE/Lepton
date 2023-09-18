import factory
from factory.django import DjangoModelFactory

from app.content.factories.toddel_factory import ToddelFactory
from app.emoji.models.toddel_emojis import ToddelEmojis


class ToddelEmojisFactory(DjangoModelFactory):
    class Meta:
        model = ToddelEmojis

    toddel = factory.SubFactory(ToddelFactory)
    emojis_allowed = factory.Faker("boolean")
