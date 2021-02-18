import factory
from factory.django import DjangoModelFactory

from app.common.enums import MembershipType
from app.content.factories import UserFactory
from app.group.factories import GroupFactory
from app.group.models import Membership


class MembershipFactory(DjangoModelFactory):
    class Meta:
        model = Membership

    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    membership_type = factory.Iterator(MembershipType)
    expiration_date = None
