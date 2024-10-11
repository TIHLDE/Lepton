import factory
from factory.django import DjangoModelFactory

from app.content.factories import UserFactory
from app.index.models.bug import Bug


class BugFactory(DjangoModelFactory):
    class Meta:
        model = Bug

    title = factory.Sequence(lambda n: f"Bug{n}")
    author = factory.SubFactory(UserFactory)
