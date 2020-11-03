import factory
from factory.django import DjangoModelFactory

from ..models import Registration
from .event_factory import EventFactory
from .user_factory import UserFactory


class RegistrationFactory(DjangoModelFactory):
    class Meta:
        model = Registration

    event = factory.SubFactory(EventFactory)
    user = factory.SubFactory(UserFactory)

    is_on_wait = factory.LazyAttribute(
        lambda registration: False
        if registration.event.limit == 0
        else registration.event.is_full
    )
