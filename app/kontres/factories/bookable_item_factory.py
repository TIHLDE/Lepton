from factory import Faker, Sequence
from factory.django import DjangoModelFactory

from app.kontres.models.bookable_item import BookableItem


class BookableItemFactory(DjangoModelFactory):
    class Meta:
        model = BookableItem

    name = Sequence(lambda n: f"Item_{n}")
    description = Faker("text")
