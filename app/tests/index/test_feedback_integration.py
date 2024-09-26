from rest_framework import status
from app.util.test_utils import get_api_client

import pytest


FEEDBACK_BASE_URL = "/index/feedbacks/"


@pytest.mark.django_db
def test_list_feedback_with_both_bug_and_idea_as_member(member, feedback_bug, feedback_idea):
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
def test_list_feedback_as_anonymous_user(default_client, feedback_bug, feedback_idea):
    """Non TIHLDE users should not be able to list feedbacks"""

    url = FEEDBACK_BASE_URL
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN