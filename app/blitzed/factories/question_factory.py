import factory
from factory.django import DjangoModelFactory

from app.blitzed.factories.drinking_game_factory import DrinkingGameFactory
from app.blitzed.models.question import Question


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question

    text = factory.Faker("sentence", nb_words=5)
    drinking_game = factory.SubFactory(DrinkingGameFactory)
