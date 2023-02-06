from datetime import timedelta

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory
from app.payment.models.paid_event import PaidEvent
from app.content.models.event import Event
from app.content.factories.event_factory import EventFactory

class PaidEventFactory(DjangoModelFactory):
    class Meta:
        model = PaidEvent
    
    price = factory.faker("pyint", min=0, max=1000)
    event = factory.SubFactory(EventFactory)
    