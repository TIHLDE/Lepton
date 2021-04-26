from datetime import timedelta

from django.db.models import signals
from django.utils import timezone

import factory
import pytest

from app.common.enums import AdminGroup
from app.forms.enums import EventFormType
from app.forms.tests.form_factories import EventFormFactory
from app.util.test_utils import get_api_client

API_EVENTS_BASE_URL = "/api/v1/events/"


def get_events_url_detail(event=None):
    return f"{API_EVENTS_BASE_URL}{event.pk}/"


def get_event_data():
    start_date = timezone.now() + timedelta(days=10)
    end_date = timezone.now() + timedelta(days=11)
    return {
        "title": "New Title",
        "location": "New Location",
        "start_date": start_date,
        "end_date": end_date,
    }


@pytest.mark.django_db
def test_list_as_anonymous_user(default_client):
    """An anonymous user should be able to list all events."""
    response = default_client.get(API_EVENTS_BASE_URL)
    assert response.status_code == 200


@pytest.mark.django_db
def test_retrieve_as_anonymous_user(default_client, event):
    """An anonymous user should be able to retrieve an event."""
    url = get_events_url_detail(event)
    response = default_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [(AdminGroup.HS, 200), (AdminGroup.INDEX, 200),],
)
def test_retrieve_as_admin_user(event, user, group_name, expected_status_code):
    """An admin user should be able to retrieve an event with more data."""
    url = get_events_url_detail(event)
    client = get_api_client(user=user, group_name=group_name)
    response = client.get(url)

    assert response.status_code == expected_status_code
    assert "evaluate_link" in response.data.keys()


@pytest.mark.django_db
def test_update_as_anonymous_user(default_client, event):
    """An anonymous user should not be able to update an event entity."""

    data = get_event_data()
    url = get_events_url_detail(event)
    response = default_client.put(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_update_as_user(event, user):
    """A user should not be able to update an event entity."""

    data = get_event_data()
    url = get_events_url_detail(event)
    client = get_api_client(user=user)
    response = client.put(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code", "new_title"),
    [
        (AdminGroup.HS, 200, "New Title"),
        (AdminGroup.INDEX, 200, "New Title"),
        (AdminGroup.NOK, 200, "New Title"),
        (AdminGroup.PROMO, 200, "New Title"),
        (AdminGroup.SOSIALEN, 200, "New Title"),
        ("Non_admin_group", 403, None),
    ],
)
@factory.django.mute_signals(signals.post_save)
def test_update_as_admin_user(event, user, group_name, expected_status_code, new_title):
    """Only users in an admin group should be able to update an event entity."""

    expected_title = new_title if new_title else event.title
    data = get_event_data()
    url = get_events_url_detail(event)
    client = get_api_client(user=user, group_name=group_name)
    response = client.put(url, data)
    event.refresh_from_db()

    assert response.status_code == expected_status_code
    assert event.title == expected_title


@pytest.mark.django_db
def test_create_as_anonymous_user(default_client):
    """An anonymous user should not be able to create an event entity."""

    data = get_event_data()
    response = default_client.post(API_EVENTS_BASE_URL, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_create_as_user(user):
    """A user should not be able to create an event entity."""

    data = get_event_data()
    client = get_api_client(user=user)
    response = client.post(API_EVENTS_BASE_URL, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, 201),
        (AdminGroup.INDEX, 201),
        (AdminGroup.NOK, 201),
        (AdminGroup.PROMO, 201),
        (AdminGroup.SOSIALEN, 201),
        ("Non_admin_group", 403),
    ],
)
def test_create_as_admin_user(user, group_name, expected_status_code):
    """Only users in an admin group should be able to create an event entity."""

    data = get_event_data()
    client = get_api_client(user=user, group_name=group_name)
    response = client.post(API_EVENTS_BASE_URL, data)
    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_delete_as_anonymous_user(default_client, event):
    """An anonymous user should not be able to delete an event entity."""
    url = get_events_url_detail(event)
    response = default_client.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_as_user(user, event):
    """A user should not be able to to delete an event entity."""
    client = get_api_client(user=user)
    url = get_events_url_detail(event)
    response = client.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, 200),
        (AdminGroup.INDEX, 200),
        (AdminGroup.NOK, 200),
        (AdminGroup.PROMO, 200),
        (AdminGroup.SOSIALEN, 200),
        ("Non_admin_group", 403),
    ],
)
def test_delete_as_group_members(event, user, group_name, expected_status_code):
    """Only users in an admin group should be able to delete an event entity."""
    client = get_api_client(user=user, group_name=group_name)
    url = get_events_url_detail(event)
    response = client.delete(url)
    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_retrieve_event_includes_form_evaluation(default_client, event):
    """Should include the id of the related form evaluation in the response."""
    evaluation = EventFormFactory(type=EventFormType.EVALUATION)
    event.forms.add(evaluation)
    event.save()
    url = get_events_url_detail(event)
    response = default_client.get(url)

    assert response.json().get("evaluation") == str(evaluation.id)


@pytest.mark.django_db
def test_retrieve_event_includes_form_survey(default_client, event):
    """Should include the id of the related form survey in the response."""
    survey = EventFormFactory(type=EventFormType.SURVEY)
    event.forms.add(survey)
    event.save()
    url = get_events_url_detail(event)
    response = default_client.get(url)

    assert response.json().get("survey") == str(survey.id)
