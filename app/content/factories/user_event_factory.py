import factory.django

from ..models import UserEvent
from .event_factory import EventFactory
from .user_factory import UserFactory


class UserEventFactory(factory.DjangoModelFactory):

    class Meta:
        model = UserEvent

    event = factory.SubFactory(EventFactory)
    user = factory.SubFactory(UserFactory)
