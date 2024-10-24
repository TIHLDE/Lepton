from rest_framework import status

import pytest

from app.common.enums import NativeMembershipType as MembershipType
from app.content.factories import RegistrationFactory
from app.forms.enums import NativeEventFormType as EventFormType
from app.forms.tests.form_factories import (
    AnswerFactory,
    EventFormFactory,
    GroupFormFactory,
    SubmissionFactory,
)
from app.group.factories import MembershipFactory
from app.util.test_utils import get_api_client

pytestmark = pytest.mark.django_db


def _get_submission_url(form):
    return f"/forms/{form.id}/submissions/"


def _get_submission_detail_url(form, submission):
    return f"/forms/{form.id}/submissions/{submission.id}/"


def _create_submission_data(field, **kwargs):
    return {
        "answers": [
            {
                "field": {"id": str(field.id)},
                **kwargs,
            }
        ],
    }


def _create_submission_data_with_selected_options_and_answer_text(
    field, option, answer_text
):
    return _create_submission_data(
        field, selected_options=[{"id": str(option.id)}], answer_text=answer_text
    )


def _create_submission_data_with_selected_options(field, option):
    return _create_submission_data(
        field, selected_options=[{"id": str(option.id), "order": option.order}]
    )


def _create_submission_data_with_text_answer(field, answer_text):
    return _create_submission_data(field, answer_text=answer_text)


@pytest.fixture()
def event_form():
    return EventFormFactory()


@pytest.fixture()
def group_form():
    return GroupFormFactory()


@pytest.fixture()
def submission(event_form):
    return SubmissionFactory(form=event_form)


@pytest.fixture()
def answer(submission, event_form):
    return AnswerFactory(submission=submission, field=event_form.fields.first())


def test_sending_both_selected_options_and_text_is_not_permitted(
    member_client, event_form, submission, answer
):
    url = _get_submission_url(answer.submission.form)
    submission_data = _create_submission_data_with_selected_options_and_answer_text(
        event_form.fields.first(),
        event_form.fields.first().options.first(),
        "I love this!",
    )

    response = member_client.post(url, submission_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_member_can_add_submission_with_options(
    member_client, event_form, submission, answer
):
    url = _get_submission_url(answer.submission.form)
    submission_data = _create_submission_data_with_selected_options(
        event_form.fields.first(), event_form.fields.first().options.first()
    )

    response = member_client.post(url, submission_data)

    assert response.status_code == status.HTTP_201_CREATED


def test_member_can_add_submission_with_answer_text(
    member_client, event_form, submission, answer
):
    url = _get_submission_url(answer.submission.form)
    submission_data = _create_submission_data_with_text_answer(
        event_form.fields.first(), "I love this!"
    )

    response = member_client.post(url, submission_data)

    assert response.status_code == status.HTTP_201_CREATED


def test_member_cannot_add_several_submissions(member_client, form):
    submission = SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_url(answer.submission.form)
    first_submission_data = _create_submission_data_with_text_answer(
        answer.submission.form.fields.first(), "This is the first time I love this!"
    )
    second_submission_data = _create_submission_data_with_text_answer(
        answer.submission.form.fields.first(), "This is the second time I love this!"
    )

    member_client.post(url, first_submission_data)
    response = member_client.post(url, second_submission_data)

    assert response.status_code == status.HTTP_409_CONFLICT


def test_cannot_create_event_form_evaluation_submission_if_not_attended(member_client):
    form = EventFormFactory(type=EventFormType.EVALUATION)
    submission = SubmissionFactory(form=form)
    AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_url(form)
    submission_data = _create_submission_data_with_selected_options(
        form.fields.first(), form.fields.first().options.first()
    )

    response = member_client.post(url, submission_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_post_submission_returns_http_status_201_created(
    member_client, event_form, submission, answer
):
    url = _get_submission_url(answer.submission.form)

    response = member_client.post(
        url, data=_create_submission_data(event_form.fields.first())
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_post_submission_to_event_form_can_overwrite_submission_if_unregistered(
    member_client, event_form, submission, answer
):
    url = _get_submission_url(answer.submission.form)

    member_client.post(url, data=_create_submission_data(event_form.fields.first()))
    response = member_client.post(
        url, data=_create_submission_data(event_form.fields.first())
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_post_submission_to_event_form_cant_overwrite_submission_if_registered(
    member, member_client, event_form
):
    submission = SubmissionFactory(user=member, form=event_form)
    answer = AnswerFactory(submission=submission, field=event_form.fields.first())
    RegistrationFactory(user=member, event=event_form.event)
    url = _get_submission_url(answer.submission.form)

    member_client.post(url, data=_create_submission_data(event_form.fields.first()))
    response = member_client.post(
        url, data=_create_submission_data(event_form.fields.first())
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize("method", ("get", "put", "patch", "delete"))
def test_submission_detail_illegal_methods_are_forbidden(
    method, member_client, event_form, submission, answer
):
    url = _get_submission_detail_url(answer.submission.form, submission)

    response = member_client.generic(method, url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "client, status_code",
    [
        (pytest.lazy_fixture("member_client"), status.HTTP_201_CREATED),
        (pytest.lazy_fixture("default_client"), status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_group_form_submission(client, status_code, group_form):
    url = _get_submission_url(group_form)

    response = client.post(url, data=_create_submission_data(group_form.fields.first()))

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "can_submit_multiple, status_code",
    [
        (True, status.HTTP_201_CREATED),
        (False, status.HTTP_409_CONFLICT),
    ],
)
def test_create_group_form_submission_when_can_submit_multiple(
    member_client, can_submit_multiple, status_code
):
    group_form = GroupFormFactory(can_submit_multiple=can_submit_multiple)
    url = _get_submission_url(group_form)

    member_client.post(url, data=_create_submission_data(group_form.fields.first()))
    response = member_client.post(
        url, data=_create_submission_data(group_form.fields.first())
    )

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "client, is_open_for_submissions, status_code",
    [
        (pytest.lazy_fixture("member_client"), True, status.HTTP_201_CREATED),
        (pytest.lazy_fixture("member_client"), False, status.HTTP_403_FORBIDDEN),
        (pytest.lazy_fixture("default_client"), True, status.HTTP_403_FORBIDDEN),
        (pytest.lazy_fixture("default_client"), False, status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_group_form_submission_when_is_open_for_submissions(
    client, is_open_for_submissions, status_code
):
    group_form = GroupFormFactory(is_open_for_submissions=is_open_for_submissions)
    url = _get_submission_url(group_form)

    response = client.post(url, data=_create_submission_data(group_form.fields.first()))

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "is_member_of_group, only_for_group_members, status_code",
    [
        (True, True, status.HTTP_201_CREATED),
        (True, False, status.HTTP_201_CREATED),
        (False, True, status.HTTP_403_FORBIDDEN),
        (False, False, status.HTTP_201_CREATED),
    ],
)
def test_create_group_form_submission_when_only_for_group_members(
    member, group, is_member_of_group, only_for_group_members, status_code
):
    group_form = GroupFormFactory(
        group=group, only_for_group_members=only_for_group_members
    )
    if is_member_of_group:
        MembershipFactory(
            user=member, group=group, membership_type=MembershipType.MEMBER
        )
    url = _get_submission_url(group_form)

    client = get_api_client(user=member)
    response = client.post(url, data=_create_submission_data(group_form.fields.first()))

    assert response.status_code == status_code


def test_create_group_form_member_can_view_submission(membership):
    group_form = GroupFormFactory(group=membership.group, only_for_group_members=True)
    url = _get_submission_url(group_form)

    client = get_api_client(user=membership.user)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
