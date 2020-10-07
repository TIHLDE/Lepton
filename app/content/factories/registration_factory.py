import factory

from ..models import Registration
from .event_factory import EventFactory
from .registration_factory import UserFactory


class RegistrationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Registration

    event = factory.SubFactory(EventFactory)
    user = factory.SubFactory(UserFactory)

    is_on_wait = factory.LazyAttribute(
        lambda registration: False
        if registration.event.limit == 0
        else registration.event.is_full()
    )
