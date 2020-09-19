import factory
from factory.django import DjangoModelFactory

from ..models import UserEvent
from .event_factory import EventFactory
from .user_factory import UserFactory


class UserEventFactory(DjangoModelFactory):

    class Meta:
        model = UserEvent

    event = factory.SubFactory(EventFactory)
    user = factory.SubFactory(UserFactory)

    is_on_wait = factory.LazyAttribute(
        lambda user_event: False if user_event.event.limit == 0 else user_event.event.is_full()
    )
