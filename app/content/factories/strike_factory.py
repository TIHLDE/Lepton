import factory
from factory.django import DjangoModelFactory

from app.content.factories.event_factory import EventFactory
from app.content.factories.user_factory import UserFactory
from app.content.models.strike import Strike


class StrikeFactory(DjangoModelFactory):
    class Meta:
        model = Strike

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    creator = factory.SubFactory(UserFactory)
