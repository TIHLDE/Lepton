from rest_framework import status

import pytest

from app.forms.tests.form_factories import (
    AnswerFactory,
    EventFormFactory,
    SubmissionFactory,
)
from app.util.test_utils import get_api_client

pytestmark = pytest.mark.django_db


def _get_submission_url(form):
    return f"/api/v1/forms/{form.id}/submission/"


def _get_submission_detail_url(form, submission):
    return f"/api/v1/forms/{form.id}/submission/{submission.id}/"


def _create_submission_data(user, field, **kwargs):
    return {
        "user": str(user.user_id),  # TODO - we should be able to remove this, but when we do... ka-boom
        "answers": [
            {
                "field": {"id": str(field.id)},
                **kwargs,
            }
        ],
    }


def _create_submission_data_with_selected_options_and_answer_text(user, field, option, answer_text):
    return _create_submission_data(user, field, selected_options=[{"id": str(option.id)}], answer_text=answer_text)


def _create_submission_data_with_selected_options(user, field, option):
    return _create_submission_data(user, field, selected_options=[{"id": str(option.id)}])


def _create_submission_data_with_text_answer(user, field, answer_text):
    return _create_submission_data(user, field, answer_text=answer_text)


def test_sending_both_selected_options_and_text_is_not_permitted(member):
    client = get_api_client(user=member)
    form = EventFormFactory()
    submission = SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_url(answer.submission.form)
    submission_data = _create_submission_data_with_selected_options_and_answer_text(
        member, form.fields.first(), form.fields.first().options.first(), "I love this!"
    )
    response = client.post(url, submission_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_member_can_add_submission_with_options(member):
    client = get_api_client(user=member)
    form = EventFormFactory()
    submission = SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_url(answer.submission.form)
    submission_data = _create_submission_data_with_selected_options(
        member, form.fields.first(), form.fields.first().options.first()
    )
    response = client.post(url, submission_data)

    assert response.status_code == status.HTTP_201_CREATED


def test_member_can_add_submission_with_answer_text(member):
    client = get_api_client(user=member)
    form = EventFormFactory()
    submission = SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_url(answer.submission.form)
    submission_data = _create_submission_data_with_text_answer(
        member, form.fields.first(), "I love this!"
    )
    response = client.post(url, submission_data)

    assert response.status_code == status.HTTP_201_CREATED


def test_member_cannot_add_several_submissions(member):
    client = get_api_client(user=member)
    form = EventFormFactory()
    submission = SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_url(answer.submission.form)
    submission_data = _create_submission_data_with_text_answer(
        member, form.fields.first(), "This is the first time I love this!"
    )
    client.post(url, submission_data)

    submission_data = _create_submission_data_with_text_answer(
        member, form.fields.first(), "This is the second time I love this!"
    )
    response = client.post(url, submission_data)

    assert response.status_code == status.HTTP_409_CONFLICT


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
