import factory
from factory.django import DjangoModelFactory

from app.content.factories.user_factory import UserFactory
from app.content.models.minute import Minute


class MinuteFactory(DjangoModelFactory):
    class Meta:
        model = Minute

    title = factory.Faker("sentence", nb_words=4)
    content = factory.Faker("text")
    author = factory.SubFactory(UserFactory)
