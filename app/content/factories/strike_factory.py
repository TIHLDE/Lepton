from datetime import timedelta

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from app.common.enums import NativeStrikeEnum as StrikeEnum
from app.content.factories.event_factory import EventFactory
from app.content.factories.user_factory import UserFactory
from app.content.models.strike import Strike


class StrikeFactory(DjangoModelFactory):
    class Meta:
        model = Strike

    user = factory.SubFactory(UserFactory)
    creator = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    description = factory.Iterator(StrikeEnum)
    strike_size = factory.Faker("pyint", min_value=1, max_value=3)
    created_at = timezone.now() - timedelta(days=1)
