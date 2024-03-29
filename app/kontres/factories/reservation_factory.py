from django.utils import timezone

from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from app.content.factories import UserFactory
from app.kontres.enums import ReservationStateEnum
from app.kontres.factories.bookable_item_factory import BookableItemFactory
from app.kontres.models.reservation import Reservation


class ReservationFactory(DjangoModelFactory):
    class Meta:
        model = Reservation

    author = SubFactory(UserFactory)
    bookable_item = SubFactory(BookableItemFactory)
    start_time = timezone.now() + timezone.timedelta(hours=1)
    end_time = timezone.now() + timezone.timedelta(hours=2)
    state = ReservationStateEnum.PENDING
    description = Faker("text")
