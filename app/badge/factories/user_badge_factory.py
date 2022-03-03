import factory
from factory.django import DjangoModelFactory

from app.badge.factories import BadgeFactory
from app.badge.models import UserBadge
from app.content.factories.user_factory import UserFactory


class UserBadgeFactory(DjangoModelFactory):
    class Meta:
        model = UserBadge

    user = factory.SubFactory(UserFactory)
    badge = factory.SubFactory(BadgeFactory)
