from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory

import pytest

from app.content.factories import EventFactory, UserFactory


@pytest.fixture()
def request_factory():
    return APIRequestFactory()


@pytest.fixture()
def user():
    return UserFactory()


@pytest.fixture()
def event():
    return EventFactory()


@pytest.fixture
def token(user):
    return Token.objects.get(user_id=user.user_id)
