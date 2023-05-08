import random
from datetime import datetime, timedelta

import factory
from factory.django import DjangoModelFactory

from app.content.factories.event_factory import EventFactory
from app.payment.models.paid_event import PaidEvent


class PaidEventFactory(DjangoModelFactory):
    class Meta:
        model = PaidEvent

    price = random.randint(0, 1000)
    event = factory.SubFactory(EventFactory)
    paytime = datetime.now() + timedelta(hours=0, minutes=1)
