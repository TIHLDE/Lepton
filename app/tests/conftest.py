from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory

import pytest

from app.content.enums import AdminGroup
from app.content.factories import (
    EventFactory,
    NewsFactory,
    RegistrationFactory,
    UserFactory,
)
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
def registration():
    return RegistrationFactory()


@pytest.fixture()
def news():
    return NewsFactory()
