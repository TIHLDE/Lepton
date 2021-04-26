from rest_framework import status

import pytest

from app.content.factories.user_factory import UserFactory
from app.util.test_utils import get_api_client


@pytest.fixture
def user():
    return UserFactory()


def _get_valid_refund_form_data():
    return {
        "images": [
            """data:image/png;base64,iVBORw0KGgoAAAANSUh
            EUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+
            hHgAHggJ/PchI7wAAAABJRU5ErkJggg==""",
            """data:image/png;base64,iVBORw0KGgoAAAANSUh
            EUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+
            hHgAHggJ/PchI7wAAAABJRU5ErkJggg==""",
        ],
        "date": "2021-04-13",
        "occasion": "pytest",
        "amount": "69",
        "comment": "Running pytest",
        "mailto": "index_test@tihlde.org",
        "name": "Index",
        "committee": "Index",
        "accountNumber": "69420666",
        "mailfrom": "index_test@tihlde.org",
    }


def _get_invalid_refund_form_data():
    return {"token_id": "test_token_id", "charge_id": "fake_charge_id"}


refund_form_url = "/api/v1/refund-form/"


@pytest.mark.django_db
def test_send_valid_refund_form_request(user):

    data = _get_valid_refund_form_data()
    client = get_api_client(user=user)

    response = client.post(refund_form_url, data=data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_send_invalid_refund_form_request(user):

    data = _get_invalid_refund_form_data()
    client = get_api_client(user=user)

    response = client.post(refund_form_url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_not_authenticated_refund_form_request(default_client):

    data = _get_valid_refund_form_data()

    response = default_client.post(refund_form_url, data=data)
    print(response)

    assert response.status_code == status.HTTP_403_FORBIDDEN
