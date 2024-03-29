import factory
from factory.django import DjangoModelFactory

from app.content.factories.event_factory import EventFactory
from app.content.factories.user_factory import UserFactory
from app.payment.enums import OrderStatus
from app.payment.models.order import Order


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    status = OrderStatus.INITIATE
    payment_link = factory.Faker("url")
