import pytest

from rest_framework import status


API_QR_CODE_BASE_URL = "/qr-codes/"


def get_data(user=None):
    return {
        "name": "Test QR Code",
        "url": "https://tihlde.org",
        "user": user.user_id if user else None
    }


@pytest.mark.django_db
def test_create_qr_code_as_member(member, api_client):
    """
        A member of TIHLDE should be able to create a QR Code.
    """

    data = get_data(user=member)

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

    client = api_client(user=member)
    response = client.delete(f"{API_QR_CODE_BASE_URL}{qr_code.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_qr_code_with_invalid_blob_as_anonymous_user(default_client, qr_code):
    """
        An anonymous user should not be able to delete a QR Code when the blob is not found.
    """
    
    response = default_client.delete(f"{API_QR_CODE_BASE_URL}{qr_code.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN