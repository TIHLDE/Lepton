import factory
from factory.django import DjangoModelFactory

from app.index.models.idea import Idea
from app.content.factories import UserFactory

class IdeaFactory(DjangoModelFactory):
    class Meta:
        model = Idea

    title = factory.Sequence(lambda n: f"Idea{n}")
    author = factory.SubFactory(UserFactory)