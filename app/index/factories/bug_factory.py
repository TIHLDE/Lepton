import factory
from factory.django import DjangoModelFactory

from app.index.models.bug import Bug
from app.content.factories import UserFactory

class BugFactory(DjangoModelFactory):
    class Meta:
        model = Bug

    title = factory.Sequence(lambda n: f"Bug{n}")
    author = factory.SubFactory(UserFactory)
