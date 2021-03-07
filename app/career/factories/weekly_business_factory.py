from random import randint

import factory
from factory.django import DjangoModelFactory

from app.career.models import WeeklyBusiness
from app.util import today


class WeeklyBusinessFactory(DjangoModelFactory):
    """Factory that creates a generic weekly business"""

    class Meta:
        model = WeeklyBusiness

    business_name = factory.Faker("name")
    body = factory.Faker("sentence", nb_words=100, variable_nb_words=True)

    year = today().year
    week = randint(1, 52)
