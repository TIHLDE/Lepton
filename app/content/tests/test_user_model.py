import pytest

from app.content.factories import RegistrationFactory, UserFactory
from app.forms.enums import NativeEventFormType as EventFormType
from app.forms.tests.form_factories import EventFormFactory, SubmissionFactory

pytestmark = pytest.mark.django_db


@pytest.fixture()
def user():
    return UserFactory()


def test_get_unanswered_evaluations_when_has_no_unanswered_evaluations_returns_no_evaluations(
    user,
):
    """
    Test that no unanswered evaluations are returned
    when the user has attended an event and answered the evaluation.
    """
    evaluation = EventFormFactory(type=EventFormType.EVALUATION)
    RegistrationFactory(event=evaluation.event, user=user, has_attended=True)
    SubmissionFactory(form=evaluation, user=user)

    unanswered_evaluations = user.get_unanswered_evaluations()

    assert not unanswered_evaluations.exists()


def test_get_unanswered_evaluations_when_has_unanswered_evaluations_returns_unanswered_evaluations(
    user,
):
    """
    Test that all unanswered evaluations are returned
    when the user has attended an event and not answered the evaluation.
    """
    evaluation = EventFormFactory(type=EventFormType.EVALUATION)
    RegistrationFactory(event=evaluation.event, user=user, has_attended=True)

    unanswered_evaluations = user.get_unanswered_evaluations()

    assert unanswered_evaluations.count() == 1


def test_has_unanswered_evaluations_when_has_no_unanswered_evaluations_returns_true(
    user,
):
    evaluation = EventFormFactory(type=EventFormType.EVALUATION)
    RegistrationFactory(event=evaluation.event, user=user, has_attended=True)
    SubmissionFactory(form=evaluation, user=user)

    has_unanswered_evaluations = user.has_unanswered_evaluations()

    assert not has_unanswered_evaluations


def test_has_unanswered_evaluations_when_has_unanswered_evaluations_returns_false(
    user,
):
    evaluation = EventFormFactory(type=EventFormType.EVALUATION)
    RegistrationFactory(event=evaluation.event, user=user, has_attended=True)

    has_unanswered_evaluations = user.has_unanswered_evaluations()

    assert has_unanswered_evaluations
