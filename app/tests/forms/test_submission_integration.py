from rest_framework import status
import pytest

from app.forms.tests.form_factories import AnswerFactory, SubmissionFactory, EventFormFactory, FieldFactory
from app.util.test_utils import get_api_client

pytestmark = pytest.mark.django_db

def _get_submission_url(form):
    return f"/api/v1/forms/{form.id}/submission/"

def _get_submission_detail_url(form, submission):
    return f"/api/v1/forms/{form.id}/submission/{submission.id}/"

def test_sending_both_selected_options_and_text_is_not_permitted(member):
    client = get_api_client(user=member)
    form = EventFormFactory()
    submission =  SubmissionFactory(form=form)
    answer = AnswerFactory(submission=submission, field=form.fields.first())
    url = _get_submission_detail_url(answer.submission.form, answer) 
    response = client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_sending_selected_options_is_permitted():
    pass

def test_sending_text_is_permitted(): 
    pass

def test_member_can_add_submission():
    pass

def test_member_cannot_add_several_submissions():
    pass

def test_post_can_only_be_done_by_members():
    pass

def test_cannot_create_event_form_evaluation_submission_if_not_attended():
    pass

def test_non_post_operations_are_not_allowed():
    pass
