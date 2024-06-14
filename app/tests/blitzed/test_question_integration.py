from django.utils import timezone
from rest_framework import status

import pytest

from app.blitzed.factories.drinking_game_factory import DrinkingGameFactory
from app.blitzed.factories.question_factory import QuestionFactory
from app.blitzed.models.question import Question
from app.common.enums import AdminGroup, Groups
from app.util.test_utils import get_api_client

API_QUESTION_BASE_URL = "/blitzed/question/"


def _get_question_url(drinking_game_id=None):
    if drinking_game_id is not None:
        return f"{API_QUESTION_BASE_URL}{drinking_game_id}/"
    return API_QUESTION_BASE_URL


def _get_question_post_data(drinking_game=None):
    if drinking_game is None:
        drinking_game = DrinkingGameFactory()
    return {
        "text": "Hvem er den fulleste personen i rommet?",
        "drinking_game": drinking_game.id,
    }


def _get_question_put_data(question):
    return {
        "id": question.id,
        "text": "Hvem er den mest edru personen i rommet?",
        "drinking_game": question.drinking_game.id,
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_201_CREATED),
        (AdminGroup.INDEX, status.HTTP_201_CREATED),
        (AdminGroup.NOK, status.HTTP_201_CREATED),
        (AdminGroup.PROMO, status.HTTP_201_CREATED),
        (AdminGroup.SOSIALEN, status.HTTP_201_CREATED),
    ],
)
def test_create_question(member, group_name, expected_status_code, drinking_game):
    """Users in admin groups should be able to create a new question for a drinking games."""
    url = _get_question_url()
    client = get_api_client(user=member, group_name=group_name)
    data = _get_question_post_data(drinking_game)
    response = client.post(url, data, format="json")

    assert response.status_code == expected_status_code
    assert Question.objects.count() == 1
    assert Question.objects.get().text == "Hvem er den fulleste personen i rommet?"


@pytest.mark.django_db
def test_list_questions(question, member):
    """A user should be able to retrieve a question."""
    url = _get_question_url()
    client = get_api_client(user=member)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    questions = response.data
    assert len(questions) == 1
    assert questions[0]["text"] == question.text


@pytest.mark.django_db
def test_list_as_anonymous(default_client):
    """An anonymous user should be able to retrieve questions."""
    url = _get_question_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name",
    list(AdminGroup.all()),
)
def test_update_question(member, question, group_name):
    """A member of an admin group user should be able to update a question for a drinking game."""
    url = _get_question_url(question.id)
    client = get_api_client(user=member, group_name=group_name)
    data = _get_question_put_data(question)
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    question.refresh_from_db()
    assert question.text == "Hvem er den mest edru personen i rommet?"


@pytest.mark.django_db
def test_update_as_anonymous(default_client, question):
    """An anonymous user should not be able to update a question."""
    data = _get_question_put_data(question)
    url = _get_question_url(question.id)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_member(member, question):
    """A member should not be able to update a question for a drinking game."""
    data = _get_question_put_data(question)
    url = _get_question_url(question.id)
    client = get_api_client(user=member)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name",
    list(AdminGroup.all()),
)
def test_delete_question_as_admin(member, question, group_name):
    """Only members of admin groups should be able to delete a question for a drinking game."""
    url = _get_question_url(question.id)
    client = get_api_client(user=member, group_name=group_name)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert Question.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (Groups.REDAKSJONEN, status.HTTP_403_FORBIDDEN),
        (Groups.JUBKOM, status.HTTP_403_FORBIDDEN),
        (Groups.TIHLDE, status.HTTP_403_FORBIDDEN),
        (Groups.FONDET, status.HTTP_403_FORBIDDEN),
    ],
)
def test_delete_question_as_non_admin(
    member, question, group_name, expected_status_code
):
    """Only members of admin groups should be able to delete a question for a drinking game."""
    url = _get_question_url(question.id)
    client = get_api_client(user=member, group_name=group_name)
    response = client.delete(url)

    assert response.status_code == expected_status_code
    assert Question.objects.count() == 1


@pytest.mark.django_db
def test_delete_question_as_member(member, question):
    """Only members of admin groups should be able to delete a question for a drinking game."""
    url = _get_question_url(question.id)
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Question.objects.count() == 1


@pytest.mark.django_db
def test_delete_question_as_non_member(default_client, question):
    """Only members of admin groups should be able to delete a question for a drinking game."""
    url = _get_question_url(question.id)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Question.objects.count() == 1


@pytest.mark.django_db
def test_ordering_of_questions():
    """Questions should be ordered by creation."""
    question1 = QuestionFactory(created_at=timezone.now())
    question2 = QuestionFactory(created_at=timezone.now() + timezone.timedelta(days=1))
    question3 = QuestionFactory(created_at=timezone.now() + timezone.timedelta(days=2))

    url = _get_question_url()
    client = get_api_client()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    questions = response.data
    assert len(questions) == 3
    assert questions[0]["id"] == question3.id
    assert questions[1]["id"] == question2.id
    assert questions[2]["id"] == question1.id
