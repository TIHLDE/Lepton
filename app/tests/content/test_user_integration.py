from datetime import timedelta

from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status

import pytest

from app.common.enums import AdminGroup, GroupType
from app.content.factories.event_factory import EventFactory
from app.content.factories.registration_factory import RegistrationFactory
from app.content.factories.strike_factory import StrikeFactory
from app.content.factories.user_factory import UserFactory
from app.content.models import User
from app.forms.enums import EventFormType
from app.forms.tests.form_factories import EventFormFactory, SubmissionFactory
from app.group.models import Group
from app.util.test_utils import add_user_to_group_with_name

pytestmark = pytest.mark.django_db

API_USER_BASE_URL = "/users/"


@pytest.fixture
def dataing():
    return Group.objects.get(slug=slugify("Dataingeniør"), type=GroupType.STUDY)


@pytest.fixture
def group2019():
    return Group.objects.get(slug="2019", type=GroupType.STUDYYEAR)


def _get_user_detail_url(user):
    return f"{API_USER_BASE_URL}{user.user_id}/"


def _get_user_events_url():
    return f"{API_USER_BASE_URL}me/events/"


def _get_user_post_data():
    return {
        "email": "ola@nordmann.org",
        "first_name": "Ola",
        "last_name": "Nordmann",
        "user_id": "olanord",
        "password": "SuperSecurePassword",
        "study": slugify("Dataingeniør"),
        "class": "2019",
    }


def _get_user_put_data():
    return {
        "allergy": "Abakus",
        "cell": "98765432",
        "email": "ola@nordmann.org",
        "first_name": "Ola",
        "gender": 1,
        "image": None,
        "last_name": "Nordmann",
        "tool": "Keyboard",
    }


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


def test_list_user_forms_returns_all_answered_forms(api_client, member, form):
    submission = SubmissionFactory(form=form, user=member)

    url = _get_user_forms_url()
    client = api_client(user=member)
    response = client.get(url).json()
    results = response.get("results")

    assert len(results) == 1

    actual_form_id = results[0].get("id")
    expected_form_id = str(submission.form.id)

    assert actual_form_id == expected_form_id


def test_list_user_forms_returns_status_200_ok(api_client, form, member):
    SubmissionFactory(form=form, user=member)
    client = api_client(user=member)
    response = client.get(_get_user_forms_url())

    assert response.status_code == status.HTTP_200_OK


def test_list_user_forms_filter_on_unanswered_returns_all_unanswered_forms(
    api_client, member
):
    """Should return all unanswered evaluations for attended events."""
    unanswered_form = EventFormFactory(type=EventFormType.EVALUATION)
    RegistrationFactory(user=member, event=unanswered_form.event, has_attended=True)

    url = f"{_get_user_forms_url()}?unanswered=true"
    client = api_client(user=member)
    response = client.get(url).json()
    results = response.get("results")

    assert len(results) == 1

    actual_form_id = results[0].get("id")
    unanswered_form_id = str(unanswered_form.id)

    assert actual_form_id == unanswered_form_id


def test_list_user_forms_filter_on_answered_returns_all_answered_forms(
    api_client, member, form
):
    """Should return all answered evaluations for attended events."""
    submission = SubmissionFactory(form=form, user=member)

    unanswered_form = EventFormFactory(type=EventFormType.EVALUATION)
    RegistrationFactory(user=member, event=unanswered_form.event, has_attended=True)

    url = f"{_get_user_forms_url()}?unanswered=false"
    client = api_client(user=member)
    response = client.get(url).json()
    results = response.get("results")

    assert len(results) == 1

    actual_form_id = results[0].get("id")
    expected_form_id = str(submission.form.id)

    assert actual_form_id == expected_form_id


@pytest.fixture
def user_and_filter_value(request, user, user_with_strike):
    return [
        (user, "false"),
        (user_with_strike, "true"),
    ][request.param]


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


@pytest.mark.parametrize(
    ("url", "status_code"),
    [
        ("/", status.HTTP_200_OK),
        ("/memberships/", status.HTTP_200_OK),
        ("/membership-histories/", status.HTTP_200_OK),
        ("/badges/", status.HTTP_200_OK),
        ("/events/", status.HTTP_200_OK),
        ("/forms/", status.HTTP_200_OK),
        ("/strikes/", status.HTTP_200_OK),
        ("/data/", status.HTTP_200_OK),
        ("/permissions/", status.HTTP_200_OK),
    ],
)
def test_user_actions_self(url, status_code, member, api_client):

    url = f"{API_USER_BASE_URL}me{url}"
    client = api_client(user=member)

    response = client.get(url)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    ("url", "status_code"),
    [
        ("/", status.HTTP_200_OK),
        ("/memberships/", status.HTTP_200_OK),
        ("/membership-histories/", status.HTTP_200_OK),
        ("/badges/", status.HTTP_200_OK),
        ("/events/", status.HTTP_404_NOT_FOUND),
        ("/forms/", status.HTTP_404_NOT_FOUND),
        ("/strikes/", status.HTTP_200_OK),
        ("/data/", status.HTTP_404_NOT_FOUND),
    ],
)
def test_user_actions_get_user_as_admin_user(
    url, status_code, user, admin_user, api_client
):
    url = f"{API_USER_BASE_URL}{user.user_id}{url}"
    client = api_client(user=admin_user)

    response = client.get(url)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    ("url", "status_code"),
    [
        ("/", status.HTTP_200_OK),
        ("/memberships/", status.HTTP_200_OK),
        ("/membership-histories/", status.HTTP_200_OK),
        ("/badges/", status.HTTP_200_OK),
        ("/events/", status.HTTP_404_NOT_FOUND),
        ("/forms/", status.HTTP_404_NOT_FOUND),
        ("/strikes/", status.HTTP_403_FORBIDDEN),
        ("/data/", status.HTTP_404_NOT_FOUND),
    ],
)
def test_user_actions_get_user_as_member(url, status_code, user, member, api_client):
    url = f"{API_USER_BASE_URL}{user.user_id}{url}"
    client = api_client(user=member)

    response = client.get(url)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    ("url", "status_code"),
    [
        ("/", status.HTTP_403_FORBIDDEN),
        ("/memberships/", status.HTTP_403_FORBIDDEN),
        ("/membership-histories/", status.HTTP_403_FORBIDDEN),
        ("/badges/", status.HTTP_403_FORBIDDEN),
    ],
)
def test_user_actions_get_user_as_not_member(
    url, status_code, user, member, api_client
):
    url = f"{API_USER_BASE_URL}{member.user_id}{url}"
    client = api_client(user=user)

    response = client.get(url)
    assert response.status_code == status_code


def test_user_detail_strikes_as_admin(admin_user, api_client):
    url = f"{API_USER_BASE_URL}{admin_user.user_id}/strikes/"
    client = api_client(user=admin_user)

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_user_detail_strikes_as_user(user, api_client):
    url = f"{API_USER_BASE_URL}{user.user_id}/strikes/"
    client = api_client(user=user)

    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_as_anonymous_user(user, api_client):
    """An anonymous user should not be able to list all users."""
    UserFactory()
    client = api_client(user=user)
    response = client.get(API_USER_BASE_URL)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_as_member(member, api_client):
    """A member should be able to list all users."""
    client = api_client(user=member)
    response = client.get(API_USER_BASE_URL)

    assert response.status_code == status.HTTP_200_OK


def test_list_as_member_of_admin_group(admin_user, api_client):
    """An admin should be able to list all users."""
    client = api_client(user=admin_user)
    response = client.get(API_USER_BASE_URL)

    assert response.status_code == status.HTTP_200_OK


def test_update_user_as_anonymous(default_client, user):
    """An anonymous user should not be able to update a user."""
    data = _get_user_put_data()
    url = _get_user_detail_url(user)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_self_as_member(member, api_client):
    """
    A member should be able to update self.
    Members should not be able to update email, names, class or study
    """
    client = api_client(user=member)
    data = _get_user_put_data()
    url = _get_user_detail_url(member)
    response = client.put(url, data)

    member.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK

    assert member.allergy == data["allergy"]
    assert member.email != data["email"]
    assert member.first_name != data["first_name"]
    assert member.last_name != data["last_name"]


def test_update_other_user_as_member(member, user, api_client):
    """A member should not be able to update other users."""
    client = api_client(user=member)
    data = _get_user_put_data()
    url = _get_user_detail_url(user)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_other_user_as_hs_user(member, user, api_client):
    """A HS member should not be able to update other users."""
    add_user_to_group_with_name(member, AdminGroup.HS)
    client = api_client(user=member)
    data = _get_user_put_data()
    url = _get_user_detail_url(user)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_other_user_as_index_user(member, user, api_client):
    """
    Members of Index should be able to update other users.
    Index should be able to update all fields.
    """
    add_user_to_group_with_name(member, AdminGroup.INDEX)
    client = api_client(user=member)
    data = _get_user_put_data()
    url = _get_user_detail_url(user)
    response = client.put(url, data)

    user.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK

    assert user.allergy == data["allergy"]
    assert user.email == data["email"]
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]


def test_create_as_anonymous(default_client):
    """An anonymous user should be able to create a new user."""
    data = _get_user_post_data()
    response = default_client.post(API_USER_BASE_URL, data)

    assert response.status_code == status.HTTP_201_CREATED


def test_create_correctly_assigns_fields(api_client):
    client = api_client()
    data = _get_user_post_data()

    client.post(API_USER_BASE_URL, data)

    user = User.objects.get(user_id=data.get("user_id"))

    assert user.email == data["email"]
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]


def test_create_adds_user_to_class_group(api_client, dataing, group2019):
    data = _get_user_post_data()
    response = api_client().post(API_USER_BASE_URL, data)

    user_id = response.json().get("detail").get("user_id")

    assert dataing.members.filter(user_id=user_id).exists()


def test_create_adds_user_to_study_group(api_client, dataing, group2019):
    data = _get_user_post_data()
    response = api_client().post(API_USER_BASE_URL, data)

    user_id = response.json().get("detail").get("user_id")

    assert group2019.members.filter(user_id=user_id).exists()


def test_that_user_can_be_created_without_any_groups(api_client):
    data = _get_user_post_data()
    data["study"] = None
    data["class"] = None

    response = api_client().post(API_USER_BASE_URL, data)

    assert response.status_code == status.HTTP_201_CREATED


def test_create_duplicate_user(default_client):
    """
    An anonymous user should not be able to create a new user
    if a user with same user_id already exists.
    """
    data = _get_user_post_data()
    UserFactory(user_id=data["user_id"])
    response = default_client.post(API_USER_BASE_URL, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_destroy_user_as_anonymous(default_client, user):
    """An anonymous user should not be able to destroy a user."""
    url = _get_user_detail_url(user)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_destroy_self_as_member(member, api_client):
    """A member should be able to destroy self."""
    client = api_client(user=member)
    url = _get_user_detail_url(member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


def test_destroy_other_user_as_member(member, user, api_client):
    """A member should not be able to destroy other users."""
    client = api_client(user=member)
    url = _get_user_detail_url(user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_destroy_other_user_as_hs_user(member, user, api_client):
    """A HS user should not be able to destroy other users."""
    add_user_to_group_with_name(member, AdminGroup.HS)
    client = api_client(user=member)
    url = _get_user_detail_url(user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_destroy_other_user_as_index_user(member, user, api_client):
    """An index user should be able to destroy other users."""
    add_user_to_group_with_name(member, AdminGroup.INDEX)
    client = api_client(user=member)
    url = _get_user_detail_url(user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_expired_user_event_shows_as_expired(member, api_client):
    """ "All the events listed as expired should be expired"""
    client = api_client(user=member)

    two_days_ago = timezone.now() - timedelta(days=2)
    event = EventFactory(end_date=two_days_ago)

    registration = RegistrationFactory(user=member, event=event)

    url = _get_user_events_url()

    query_params = {"expired": "true"}

    response = client.get(url, data=query_params)

    assert response.status_code == status.HTTP_200_OK

    registrations = response.json().get("results")
    for registration in registrations:
        assert registration.get("expired") == True
