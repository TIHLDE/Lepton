from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory

import pytest

from app.badge.factories import BadgeFactory, UserBadgeFactory
from app.career.factories import WeeklyBusinessFactory
from app.codex.factories import CodexEventFactory, CodexEventRegistrationFactory
from app.common.enums import AdminGroup, Groups
from app.common.enums import NativeMembershipType as MembershipType
from app.communication.factories import (
    BannerFactory,
    NotificationFactory,
    UserNotificationSettingFactory,
)
from app.content.factories import (
    CheatsheetFactory,
    EventFactory,
    MinuteFactory,
    NewsFactory,
    PageFactory,
    ParentPageFactory,
    PriorityPoolFactory,
    QRCodeFactory,
    RegistrationFactory,
    ShortLinkFactory,
    UserBioFactory,
    UserFactory,
)
from app.content.factories.toddel_factory import ToddelFactory
from app.emoji.factories.reaction_factory import (
    EventReactionFactory,
    NewsReactionFactory,
)
from app.feedback.factories import BugFactory, IdeaFactory
from app.files.models.user_gallery import UserGallery
from app.forms.tests.form_factories import FormFactory, SubmissionFactory
from app.group.factories import GroupFactory, MembershipFactory
from app.group.factories.fine_factory import FineFactory
from app.group.factories.membership_factory import MembershipHistoryFactory
from app.kontres.factories import BookableItemFactory, ReservationFactory
from app.payment.factories.order_factory import OrderFactory
from app.payment.factories.paid_event_factory import PaidEventFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client


def _add_user_to_group(user, group):
    return MembershipFactory(
        user=user, group=group, membership_type=MembershipType.MEMBER
    )


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


@pytest.fixture()
def qr_code():
    return QRCodeFactory()


@pytest.fixture
def token(user):
    return Token.objects.get(user_id=user.user_id)


@pytest.fixture()
def admin_user(member):
    add_user_to_group_with_name(member, AdminGroup.HS)
    return member


@pytest.fixture()
def nok_user(member):
    add_user_to_group_with_name(member, AdminGroup.NOK)
    return member


@pytest.fixture()
def sosialen_user(member):
    add_user_to_group_with_name(member, AdminGroup.SOSIALEN)
    return member


@pytest.fixture()
def member():
    user = UserFactory()
    add_user_to_group_with_name(user, Groups.TIHLDE)
    return user


@pytest.fixture()
def jubkom_member(member):
    add_user_to_group_with_name(member, Groups.JUBKOM)
    return member


@pytest.fixture()
def plask_member(member):
    add_user_to_group_with_name(member, Groups.PLASK)
    return member


@pytest.fixture()
def index_member(member):
    add_user_to_group_with_name(member, AdminGroup.INDEX)
    return member


@pytest.fixture()
def member_client(member):
    return get_api_client(user=member)


@pytest.fixture()
def event():
    return EventFactory()


@pytest.fixture()
def paid_event():
    return PaidEventFactory()


@pytest.fixture()
def group():
    return GroupFactory()


@pytest.fixture()
def order():
    return OrderFactory()


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
def banner():
    return BannerFactory()


@pytest.fixture()
def toddel():
    return ToddelFactory()


@pytest.fixture()
def bookable_item():
    return BookableItemFactory()


@pytest.fixture()
def reservation():
    return ReservationFactory()


@pytest.fixture()
def news_reaction(member, news):
    return NewsReactionFactory(user=member, content_object=news)


@pytest.fixture()
def event_reaction(member, event):
    return EventReactionFactory(user=member, content_object=event)


@pytest.fixture()
def priority_group():
    return GroupFactory(name="Prioritized group", slug="prioritized_group")


@pytest.fixture()
def user_in_priority_pool(priority_group):
    user = UserFactory()
    _add_user_to_group(user, priority_group)
    return user


@pytest.fixture()
def event_with_priority_pool(priority_group):
    event = EventFactory(limit=1)
    PriorityPoolFactory(event=event, groups=(priority_group,))
    return event


@pytest.fixture()
def user_bio():
    return UserBioFactory()


@pytest.fixture()
def minute(user):
    return MinuteFactory(author=user)


@pytest.fixture()
def codex_event():
    return CodexEventFactory()


@pytest.fixture()
def codex_event_registration():
    return CodexEventRegistrationFactory()


@pytest.fixture
def user_gallery(member):
    """Creates a gallery for the member."""
    return UserGallery.objects.create(author=member)


@pytest.fixture
def admin_gallery(admin_user):
    """Creates a gallery for the admin user."""
    return UserGallery.objects.create(author=admin_user)


@pytest.fixture()
def new_admin_user():
    admin = UserFactory()
    add_user_to_group_with_name(admin, AdminGroup.HS)
    return admin


@pytest.fixture()
def feedback_bug():
    return BugFactory()


@pytest.fixture()
def feedback_idea():
    return IdeaFactory()
