from rest_framework import status

import pytest

from app.content.models import QRCode

API_QR_CODE_BASE_URL = "/qr-codes/"


def get_data():
    return {"name": "Test QR Code", "url": "https://tihlde.org"}


@pytest.mark.django_db
def test_list_qr_codes_as_anonymous_user(default_client):
    """
    An anonymous user should not be able to list QR Codes.
    """

    response = default_client.get(API_QR_CODE_BASE_URL)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_qr_codes_as_member(member, api_client):
    """
    A member of TIHLDE should be able to list QR Codes.
    """

    client = api_client(user=member)
    response = client.get(API_QR_CODE_BASE_URL)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_qr_code_as_member(member, api_client):
    """
    A member of TIHLDE should be able to create a QR Code.
    """

    data = get_data()

    client = api_client(user=member)
    response = client.post(API_QR_CODE_BASE_URL, data=data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_qr_code_as_anonymous_user(default_client):
    """
    An anonymous user should not be able to create a QR Code.
    """

    data = get_data()

    response = default_client.post(API_QR_CODE_BASE_URL, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_qr_code_with_invalid_blob_as_member(member, api_client, qr_code):
    """
    A member of TIHLDE should be able to delete a QR Code when the blob is not found.
    """

    qr_code.user = member
    qr_code.save()

    client = api_client(user=member)
    response = client.delete(f"{API_QR_CODE_BASE_URL}{qr_code.id}/")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_qr_code_with_invalid_blob_as_anonymous_user(default_client, qr_code):
    """
    An anonymous user should not be able to delete a QR Code when the blob is not found.
    """

    response = default_client.delete(f"{API_QR_CODE_BASE_URL}{qr_code.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN
