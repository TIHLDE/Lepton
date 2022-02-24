import factory
from factory.django import DjangoModelFactory

from app.badge.models.badge_category import BadgeCategory


class BadgeCategoryFactory(DjangoModelFactory):
    class Meta:
        model = BadgeCategory

    name = factory.Sequence(lambda n: f"Category{n}")
