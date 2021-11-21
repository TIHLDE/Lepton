import uuid

import factory
from factory.django import DjangoModelFactory

from app.content.factories.user_factory import UserFactory
from app.content.models.badge import Badge
from app.content.models.badge_category import BadgeCategory
from app.content.models.user_badge import UserBadge


class BadgeCategoryFactory(DjangoModelFactory):
    class Meta:
        model = BadgeCategory

    name = factory.Sequence(lambda n: f"Category{n}")


class BadgeFactory(DjangoModelFactory):
    class Meta:
        model = Badge

    id = uuid.uuid4()
    title = factory.Sequence(lambda n: f"Category{n}")
    badge_category = factory.SubFactory(BadgeCategoryFactory)


class UserBadgeFactory(DjangoModelFactory):
    class Meta:
        model = UserBadge

    user = factory.SubFactory(UserFactory)
    badge = factory.SubFactory(BadgeFactory)
