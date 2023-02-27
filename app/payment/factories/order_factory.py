import random
from datetime import timedelta

import factory
from factory.django import DjangoModelFactory

from app.content.factories.event_factory import EventFactory
from app.content.factories.user_factory import UserFactory
from app.payment.enums import OrderStatus
from app.payment.models.order import Order
from app.util.utils import now


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    status = random.choice([e.value for e in OrderStatus])
    expire_date = now() + timedelta(hours=1)
