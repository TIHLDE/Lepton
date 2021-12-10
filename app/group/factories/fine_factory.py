import factory
from factory.django import DjangoModelFactory

from app.content.factories import UserFactory
from app.group.factories import GroupFactory
from app.group.models import Fine


class FineFactory(DjangoModelFactory):
    """Factory that creates a generic Fine"""

    class Meta:
        model = Fine

    user = factory.SubFactory(UserFactory)
    created_by = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    reason = factory.Faker("sentence", nb_words=100, variable_nb_words=True)
    description = factory.Faker("word")
    payed = False
    approved = False
