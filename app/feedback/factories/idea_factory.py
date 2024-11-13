import factory
from factory.django import DjangoModelFactory

from app.content.factories import UserFactory
from app.feedback.models.idea import Idea


class IdeaFactory(DjangoModelFactory):
    class Meta:
        model = Idea

    title = factory.Sequence(lambda n: f"Idea{n}")
    author = factory.SubFactory(UserFactory)
    description = factory.Faker("text")
