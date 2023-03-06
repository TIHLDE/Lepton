import random

import factory
from factory.django import DjangoModelFactory
from datetime import time
from app.content.factories.event_factory import EventFactory
from app.payment.models.paid_event import PaidEvent


class PaidEventFactory(DjangoModelFactory):
    class Meta:
        model = PaidEvent

    price = random.randint(0, 1000)
    event = factory.SubFactory(EventFactory)
    paytime = time(hour=1)
