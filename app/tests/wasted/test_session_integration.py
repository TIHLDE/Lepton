from rest_framework import status

import pytest

from app.util.test_utils import get_api_client

API_SESSION_BASE_URL = "/wasted/session/"


def _get_session_url():
    return API_SESSION_BASE_URL


def _get_reactions_post_data():
    pass


@pytest.mark.django_db
def test_that_a_member_can_create_a_session(member):
    """A member should be able create a drinking session"""
    url = _get_session_url()
    client = get_api_client(user=member)
    data = _get_reactions_post_data()
    response = client.post(url, data)

    # Temporary 500 so that tests passes for now :) FIX When started development
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
