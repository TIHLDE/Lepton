from rest_framework import status

import pytest

from app.feedback.factories.bug_factory import BugFactory
from app.feedback.factories.idea_factory import IdeaFactory
from app.util.test_utils import get_api_client

FEEDBACK_BASE_URL = "/feedbacks/"


def get_data(type):
    return {
        "feedback_type": type,
        "title": "This is a type title",
        "description": f"This is a {type} report",
    }


@pytest.mark.django_db
def test_list_feedback_with_both_bug_and_idea_as_member(
    member, feedback_bug, feedback_idea
):
    """All members should be able to list all types of feedbacks."""

    url = FEEDBACK_BASE_URL
    client = get_api_client(member)
    response = client.get(url)

    data = response.data
    results = data["results"]
    bug_type = list(filter(lambda x: "Bug" == x["feedback_type"], results))
    idea_type = list(filter(lambda x: "Idea" == x["feedback_type"], results))

    assert response.status_code == status.HTTP_200_OK
    assert data["count"] == 2
    assert bug_type
    assert idea_type


@pytest.mark.django_db
def test_list_feedback_as_anonymous_user(default_client):
    """Non TIHLDE users should not be able to list feedbacks"""

    url = FEEDBACK_BASE_URL
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    "type",
    ["Bug", "Idea"],
)
def test_create_feedback_with_both_bug_and_idea_as_member(member, type):
    """All members should be able to create a bug and a idea feedback"""

    url = FEEDBACK_BASE_URL
    client = get_api_client(member)
    data = get_data(type)
    response = client.post(url, data=data)
    data = response.data

    assert response.status_code == status.HTTP_201_CREATED
    assert data["feedback_type"] == type


@pytest.mark.django_db
def test_create_feedback_with_wrong_type_as_member(member):
    """No members should be able to create feedback of another type than bug and idea"""

    url = FEEDBACK_BASE_URL
    client = get_api_client(member)
    data = get_data("wrong_type")
    response = client.post(url, data=data)
    data = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize(
    "type",
    ["Bug", "Idea"],
)
def test_create_feedback_as_anonymous_user(default_client, type):
    """Non TIHLDE users should not be able to create feedbacks"""

    url = FEEDBACK_BASE_URL
    data = get_data(type)
    response = default_client.post(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    "type",
    ["Bug", "Idea"],
)
def test_update_feedback_with_both_bug_and_idea_as_member(member, type):
    """All members should be able to update their own bug and idea feedback"""

    url = FEEDBACK_BASE_URL
    data = get_data(type)
    client = get_api_client(member)
    response = client.post(url, data=data)
    data = response.data

    assert response.status_code == status.HTTP_201_CREATED
    assert data["feedback_type"] == type


@pytest.mark.django_db
@pytest.mark.parametrize(
    "type",
    ["Bug", "Idea"],
)
def test_destroy_feedback_as_index_user(index_member, type):
    """An Index user should be able to delete other members feedback"""

    url = FEEDBACK_BASE_URL
    data = get_data(type)
    client = get_api_client(user=index_member)

    initial_response = client.post(url, data=data)

    feedback_id = initial_response.data["id"]

    url = f"{FEEDBACK_BASE_URL}{feedback_id}/"

    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    "type",
    ["Bug", "Idea"],
)
def test_destroy_your_own_feedback_as_member(member, type):
    """A user should be able to delete their own feedback as a member"""

    url = FEEDBACK_BASE_URL
    data = get_data(type)
    client = get_api_client(user=member)

    initial_response = client.post(url, data=data)

    print(initial_response.data)
    print(f"Author: {initial_response.data['author']}")

    feedback_id = initial_response.data["id"]

    url = f"{FEEDBACK_BASE_URL}{feedback_id}/"

    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    "type",
    ["Bug", "Idea"],
)
def test_destroy_feedback_as_anonymous_user(default_client, type):
    """Non TIHLDE users should not be able to delete feedbacks"""

    url = FEEDBACK_BASE_URL
    data = get_data(type)
    response = default_client.delete(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_bug_as_member(member):
    """A member should be able to retrieve a bug feedback"""
    feedback_bug = BugFactory(author=member)

    url = f"{FEEDBACK_BASE_URL}{feedback_bug.id}/"
    client = get_api_client(member)
    response = client.get(url)

    assert response.data["feedback_type"] == "Bug"
    assert response.data["url"] == feedback_bug.url
    assert response.data["browser"] == feedback_bug.browser
    assert response.data["platform"] == feedback_bug.platform
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_idea_as_member(member):
    """A member should be able to retrieve an idea feedback"""
    feedback_idea = IdeaFactory(author=member)

    url = f"{FEEDBACK_BASE_URL}{feedback_idea.id}/"
    client = get_api_client(member)
    response = client.get(url)

    assert response.data["feedback_type"] == "Idea"
    assert response.status_code == status.HTTP_200_OK
