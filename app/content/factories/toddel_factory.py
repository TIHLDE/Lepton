import factory
from factory.django import DjangoModelFactory

from app.content.models import Toddel


class ToddelFactory(DjangoModelFactory):
    class Meta:
        model = Toddel

    edition = 1
    title = factory.Faker("sentence", nb_words=5)
    image = factory.Faker("uri")
    pdf = factory.Faker("uri")
    published_at = factory.Faker("date_object")
