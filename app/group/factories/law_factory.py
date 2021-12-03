import factory
from factory.django import DjangoModelFactory

from app.group.factories.group_factory import GroupFactory
from app.group.models.law import Law


class LawFactory(DjangoModelFactory):
    """Factory that creates a generic group"""

    class Meta:
        model = Law

    group = factory.SubFactory(GroupFactory)
    description = factory.Faker("sentence", nb_words=100, variable_nb_words=True)
    paragraph = factory.Faker("word")
    amount = 1
