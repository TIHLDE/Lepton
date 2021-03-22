from rest_framework import status

import pytest

from app.forms.models.forms import Form, Submission
from app.forms.tests.form_factories import (
    AnswerFactory,
    EventFormFactory,
    FieldFactory,
    SubmissionFactory,
)
from app.util.test_utils import get_api_client

pytestmark = pytest.mark.django_db


def _get_submission_url(form):
    return f"/api/v1/forms/{form.id}/submission/"


def _get_submission_detail_url(form, submission):
    return f"/api/v1/forms/{form.id}/submission/{submission.id}/"


def _create_submission_data(user, field, option, text_answer):
    return {
        "user": str(user.user_id),
        "answers": [
            {
                "field": {"id": str(field.id)},
                "selected_options": [{"id": str(option.id)}],
                "text_answer": text_answer,
            }
        ],
    }


def test_sending_both_selected_options_and_text_is_not_permitted(member):
    client = get_api_client(user=member)
    form = EventFormFactory()
    submission = SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_url(answer.submission.form)
    submission_data = _create_submission_data(
        member, form.fields.first(), form.fields.first().options.first(), "I love this!"
    )
    response = client.post(url, submission_data)

    print(response.json())

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_sending_selected_options_is_permitted():
    pass


def test_sending_text_is_permitted():
    pass


def test_member_can_add_submission():
    pass


def test_member_cannot_add_several_submissions():
    pass


def test_cannot_create_event_form_evaluation_submission_if_not_attended():
    pass


def test_post_can_only_be_done_by_members():
    client = get_api_client()
    form = EventFormFactory()
    submission = SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_detail_url(answer.submission.form, submission)

    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_operations_are_not_allowed(member):
    client = get_api_client(user=member)
    form = EventFormFactory()
    submission = SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_detail_url(answer.submission.form, submission)

    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_put_operations_are_not_allowed(member):
    client = get_api_client(user=member)
    form = EventFormFactory()
    submission = SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_detail_url(answer.submission.form, submission)

    response = client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_patch_operations_are_not_allowed(member):
    client = get_api_client(user=member)
    form = EventFormFactory()
    submission = SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_detail_url(answer.submission.form, submission)

    response = client.patch(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_operations_are_not_allowed(member):
    client = get_api_client(user=member)
    form = EventFormFactory()
    submission = SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_detail_url(answer.submission.form, submission)

    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
