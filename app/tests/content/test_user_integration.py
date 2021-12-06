from datetime import timedelta

from rest_framework import status

import pytest

from app.content.factories.badge_factory import BadgeFactory, UserBadgeFactory
from app.content.factories.registration_factory import RegistrationFactory
from app.content.factories.strike_factory import StrikeFactory
from app.content.factories.user_factory import UserFactory
from app.forms.enums import EventFormType
from app.forms.tests.form_factories import EventFormFactory
from app.util.utils import now

pytestmark = pytest.mark.django_db

API_USER_BASE_URL = "/user/"


def _get_user_forms_url():
    return f"{API_USER_BASE_URL}me/forms/"


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def user_with_strike():
    user = UserFactory()
    user.strikes.add(StrikeFactory())
    user.save()
    return user


def test_list_user_forms_returns_all_answered_forms(api_client, submission):
    user = submission.user

    url = _get_user_forms_url()
    client = api_client(user=user)
    response = client.get(url).json()
    results = response.get("results")

    assert len(results) == 1

    actual_form_id = results[0].get("id")
    expected_form_id = str(submission.form.id)

    assert actual_form_id == expected_form_id


def test_list_user_forms_returns_status_200_ok(api_client, submission):
    user = submission.user
    client = api_client(user=user)
    response = client.get(_get_user_forms_url())

    assert response.status_code == status.HTTP_200_OK


def test_list_user_forms_filter_on_unanswered_returns_all_unanswered_forms(
    api_client, submission
):
    """Should return all unanswered evaluations for attended events."""
    user = submission.user
    unanswered_form = EventFormFactory(type=EventFormType.EVALUATION)
    RegistrationFactory(user=user, event=unanswered_form.event, has_attended=True)

    url = f"{_get_user_forms_url()}?unanswered=true"
    client = api_client(user=user)
    response = client.get(url).json()
    results = response.get("results")

    assert len(results) == 1

    actual_form_id = results[0].get("id")
    unanswered_form_id = str(unanswered_form.id)

    assert actual_form_id == unanswered_form_id


def test_list_user_forms_filter_on_answered_returns_all_answered_forms(
    api_client, submission
):
    """Should return all answered evaluations for attended events."""
    user = submission.user

    unanswered_form = EventFormFactory(type=EventFormType.EVALUATION)
    RegistrationFactory(user=user, event=unanswered_form.event, has_attended=True)

    url = f"{_get_user_forms_url()}?unanswered=false"
    client = api_client(user=user)
    response = client.get(url).json()
    results = response.get("results")

    assert len(results) == 1

    actual_form_id = results[0].get("id")
    expected_form_id = str(submission.form.id)

    assert actual_form_id == expected_form_id


@pytest.fixture
def user_and_filter_value(request, user, user_with_strike):
    return [(user, "false"), (user_with_strike, "true"),][request.param]


@pytest.mark.django_db
@pytest.mark.parametrize("user_and_filter_value", [0, 1], indirect=True)
def test_filter_only_users_with_active_strikes(
    api_client, admin_user, user_and_filter_value
):
    test_user, has_strikes = user_and_filter_value
    url = f"{API_USER_BASE_URL}?has_active_strikes={has_strikes}"
    client = api_client(user=admin_user)

    response = client.get(url).json()
    results = response.get("results")
    expected_user_id = str(test_user.user_id)
    found = False
    for result in results:
        actual_user_id = result.get("user_id")
        if actual_user_id == expected_user_id:
            found = True
    assert found


@pytest.mark.django_db
def test_only_public_badges_are_shown(member, default_client):
    badge0 = BadgeFactory(title="public", active_to=now() - timedelta(1))
    UserBadgeFactory(user=member, badge=badge0)

    badge1 = BadgeFactory(title="not_public", active_to=now() + timedelta(1))
    UserBadgeFactory(user=member, badge=badge1)

    url = f"{API_USER_BASE_URL}{member.user_id}/badges/"
    response = default_client.get(url).json()

    assert response["results"][0]["title"] == "public"
    assert len(response["results"]) == 1
