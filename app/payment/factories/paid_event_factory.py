from datetime import timedelta

from django.utils import timezone

import factory, random
from factory.django import DjangoModelFactory
from app.payment.models.paid_event import PaidEvent
from app.content.models.event import Event
from app.content.factories.event_factory import EventFactory

class PaidEventFactory(DjangoModelFactory):
    class Meta:
        model = PaidEvent
    
    price = random.randint(0, 1000)
    event = factory.SubFactory(EventFactory)
    