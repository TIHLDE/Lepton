from datetime import timedelta

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from app.common.enums import NativeMembershipType as MembershipType
from app.content.factories import UserFactory
from app.group.factories import GroupFactory
from app.group.models import Membership, MembershipHistory


class MembershipFactory(DjangoModelFactory):
    class Meta:
        model = Membership

    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    membership_type = factory.Iterator(MembershipType)
    expiration_date = None


class MembershipHistoryFactory(DjangoModelFactory):
    class Meta:
        model = MembershipHistory

    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    membership_type = factory.Iterator(MembershipType)
    start_date = timezone.now() - timedelta(days=10)
    end_date = timezone.now() + timedelta(days=10)
