from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory

import pytest

from app.career.factories import WeeklyBusinessFactory
from app.common.enums import AdminGroup, MembershipType
from app.content.factories import (
    CheatsheetFactory,
    EventFactory,
    NewsFactory,
    NotificationFactory,
    PageFactory,
    ParentPageFactory,
    RegistrationFactory,
    ShortLinkFactory,
    UserFactory,
)
from app.group.factories import GroupFactory, MembershipFactory
from app.util.test_utils import add_user_to_group_with_name


@pytest.fixture()
def request_factory():
    return APIRequestFactory()


@pytest.fixture()
def default_client():
    return APIClient()


@pytest.fixture()
def user():
    return UserFactory()


@pytest.fixture
def token(user):
    return Token.objects.get(user_id=user.user_id)


@pytest.fixture()
def admin_user():
    return add_user_to_group_with_name(UserFactory(), AdminGroup.HS)


@pytest.fixture()
def member():
    return UserFactory(is_TIHLDE_member=True)


@pytest.fixture()
def event():
    return EventFactory()


@pytest.fixture()
def group():
    return GroupFactory()


@pytest.fixture()
def membership():
    return MembershipFactory(membership_type=MembershipType.MEMBER)


@pytest.fixture()
def membership_leader():
    return MembershipFactory(membership_type=MembershipType.LEADER)


@pytest.fixture
def registration():
    return RegistrationFactory()


@pytest.fixture()
def cheatsheet():
    return CheatsheetFactory()


@pytest.fixture()
def news():
    return NewsFactory()


@pytest.fixture()
def page():
    return PageFactory()


@pytest.fixture()
def parent_page():
    return ParentPageFactory()


@pytest.fixture()
def short_link():
    return ShortLinkFactory()


@pytest.fixture()
def notification():
    return NotificationFactory()
  
@pytest.fixture()
def weekly_business():
    return WeeklyBusinessFactory()
