import factory
from factory.django import DjangoModelFactory

from app.content.factories import UserFactory
from app.feedback.models.feedback import Feedback


class FeedbackFactory(DjangoModelFactory):
    class Meta:
        model = Feedback

    title = factory.Sequence(lambda n: f"Idea{n}")
    author = factory.SubFactory(UserFactory)
    description = factory.Faker("text")
