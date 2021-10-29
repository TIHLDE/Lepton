from random import randint

import factory
from factory.django import DjangoModelFactory

from app.career.models import WeeklyBusiness
from app.util import now


class WeeklyBusinessFactory(DjangoModelFactory):
    class Meta:
        model = WeeklyBusiness

    business_name = factory.Faker("name")
    body = factory.Faker("sentence", nb_words=100, variable_nb_words=True)

    year = now().year + 1
    week = randint(1, 52)
