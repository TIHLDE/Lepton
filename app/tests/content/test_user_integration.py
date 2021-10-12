from rest_framework import status

import pytest

from app.content.factories import RegistrationFactory
from app.forms.enums import EventFormType
from app.forms.tests.form_factories import EventFormFactory

pytestmark = pytest.mark.django_db

API_USER_BASE_URL = "/api/v1/user/"

def _get_user_forms_url():
    return f"{API_USER_BASE_URL}me/forms/"



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
