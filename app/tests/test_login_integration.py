from rest_framework import status

import pytest

pytestmark = pytest.mark.django_db


def test_login_when_user_with_user_id_does_not_exist(default_client):
    """Should return a 401 HTTP status if a user with the provided user id does not exist."""
    data = {"user_id": "Test", "password": "Testing123"}

    response = default_client.post(path="/api/v1/auth/login/", data=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
