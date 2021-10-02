from app.content.factories.event_factory import EventFactory
from app.content.factories.user_factory import UserFactory
from app.content.models.strike import Strike
from factory.django import DjangoModelFactory
import factory


class StrikeFactory(DjangoModelFactory):
    class Meta:
        model = Strike

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    creator = factory.SubFactory(UserFactory)