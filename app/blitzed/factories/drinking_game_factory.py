import factory
from factory.django import DjangoModelFactory

from app.blitzed.models.drinking_game import DrinkingGame


class DrinkingGameFactory(DjangoModelFactory):
    class Meta:
        model = DrinkingGame

    name = factory.Faker("sentence", nb_words=5)
    description = factory.Faker("text")
    icon = factory.Faker("uri")
