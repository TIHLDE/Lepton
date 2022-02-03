import factory
from factory.django import DjangoModelFactory

from app.badge.factories.badge_category_factory import BadgeCategoryFactory
from app.badge.models.badge import Badge


class BadgeFactory(DjangoModelFactory):
    class Meta:
        model = Badge

    title = factory.Sequence(lambda n: f"Category{n}")
    badge_category = factory.SubFactory(BadgeCategoryFactory)
