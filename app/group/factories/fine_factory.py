import factory
from factory.django import DjangoModelFactory
from app.content.factories import UserFactory
from app.group.factories import GroupFactory


from app.group.models import Fine


class FineFactory(DjangoModelFactory):
    """Factory that creates a generic group"""

    class Meta:
        model = Fine

    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    description = factory.Faker("sentence", nb_words=100, variable_nb_words=True)