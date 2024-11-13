import factory
from factory.django import DjangoModelFactory

from app.content.factories import UserFactory
from app.feedback.models.bug import Bug


class BugFactory(DjangoModelFactory):
    class Meta:
        model = Bug

    title = factory.Sequence(lambda n: f"Bug{n}")
    author = factory.SubFactory(UserFactory)
    description = factory.Faker("text")
    url = factory.Faker("url")
    platform = factory.Faker("word")
    browser = factory.Faker("word")
