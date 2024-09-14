import factory
from factory.django import DjangoModelFactory

from app.content.factories.user_factory import UserFactory
from app.content.models.minute import Minute
from app.group.factories.group_factory import GroupFactory


class MinuteFactory(DjangoModelFactory):
    class Meta:
        model = Minute

    title = factory.Faker("sentence", nb_words=4)
    content = factory.Faker("text")
    author = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
