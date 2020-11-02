import factory
from factory.django import DjangoModelFactory

from app.common.enums import GroupType
from app.group.models import Group


class GroupFactory(DjangoModelFactory):
    """Factory that creates a generic group"""

    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f"Group{n}")
    slug = factory.Sequence(lambda n: f"Group{n}")
    description = factory.Faker("sentence", nb_words=100, variable_nb_words=True)
    contact_email = factory.LazyAttributeSequence(
        lambda o, n: f"{o.slug}@{n}.example.com"
    )
    type = factory.Iterator(GroupType)
