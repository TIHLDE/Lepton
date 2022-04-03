from app.group.factories.membership_factory import MembershipHistoryFactory
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory

import pytest

from app.badge.factories import BadgeFactory, UserBadgeFactory
from app.career.factories import WeeklyBusinessFactory
from app.common.enums import AdminGroup, Groups, MembershipType
from app.communication.factories import (
    NotificationFactory,
    UserNotificationSettingFactory,
)
from app.content.factories import (
    CheatsheetFactory,
    EventFactory,
    NewsFactory,
    PageFactory,
    ParentPageFactory,
    RegistrationFactory,
    ShortLinkFactory,
    UserFactory,
)
from app.content.factories.toddel_factory import ToddelFactory
from app.forms.tests.form_factories import FormFactory, SubmissionFactory
from app.group.factories import GroupFactory, MembershipFactory
from app.group.factories.fine_factory import FineFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client


@pytest.fixture()
def request_factory():
    return APIRequestFactory()


@pytest.fixture()
def default_client():
    return get_api_client()


@pytest.fixture
def api_client():
    """
    Provide a callable fixture that returns an `APIClient` object.
    If a user is provided when calling the fixture,
    the client will be authenticated on behalf of it.

    `api_client()` -> anonymous request
    `api_client(user=user)` -> authenticated request
    `api_client(user=user, group_name=group_name)` -> authenticated request with group permissions
    """

    def _get_api_client(user=None, group_name=None):
        return get_api_client(user=user, group_name=group_name)

    return _get_api_client


@pytest.fixture()
def user():
    return UserFactory()


@pytest.fixture
def token(user):
    return Token.objects.get(user_id=user.user_id)


@pytest.fixture()
def admin_user(member):
    add_user_to_group_with_name(member, AdminGroup.HS)
    return member


@pytest.fixture()
def member():
    user = UserFactory()
    add_user_to_group_with_name(user, Groups.TIHLDE)
    return user


@pytest.fixture()
def member_client(member):
    return get_api_client(user=member)


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


@pytest.fixture()
def membership_history():
    return MembershipHistoryFactory()


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
def badge():
    return BadgeFactory()


@pytest.fixture()
def user_badge():
    return UserBadgeFactory()


@pytest.fixture()
def form():
    return FormFactory()


@pytest.fixture()
def submission(form):
    return SubmissionFactory(form=form)


@pytest.fixture()
def short_link():
    return ShortLinkFactory()


@pytest.fixture()
def notification():
    return NotificationFactory()


@pytest.fixture()
def user_notification_setting():
    return UserNotificationSettingFactory()


@pytest.fixture()
def weekly_business():
    return WeeklyBusinessFactory()


@pytest.fixture()
def fine():
    return FineFactory()


@pytest.fixture()
def toddel():
    return ToddelFactory()
