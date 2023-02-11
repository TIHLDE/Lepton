from datetime import timedelta

from django.utils import timezone
from app.util.utils import now

import factory
from factory.django import DjangoModelFactory
from app.payment.models.order import Order
from app.content.factories.user_factory import UserFactory
from app.content.factories.event_factory import EventFactory
from app.payment.enums import OrderStatus
import random

class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    order_id = "".join([str(random.randint(0, 10)) for _ in range(24)])
    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    status = random.choice([e.value for e in OrderStatus])
    expire_date = now() + timedelta(hours=1)
