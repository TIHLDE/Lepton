import factory

from app.feedback.factories.feedback_factory import FeedbackFactory
from app.feedback.models.bug import Bug


class BugFactory(FeedbackFactory):
    class Meta:
        model = Bug

    url = factory.Faker("url")
    platform = factory.Faker("word")
    browser = factory.Faker("word")
