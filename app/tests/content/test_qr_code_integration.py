from rest_framework import status

import pytest

from app.common.permissions import AdminGroup
from app.content.factories import QRCodeFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client

API_QR_CODE_BASE_URL = "/qr-codes/"


def get_data():
    return {"name": "Test QR Code", "content": "https://tihlde.org"}


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
    A member of TIHLDE should be able to list QR Codes owned by themself.
    """

    QRCodeFactory(user=member)
    QRCodeFactory(user=member)
    QRCodeFactory()

    client = api_client(user=member)
    response = client.get(API_QR_CODE_BASE_URL)

    data = response.data["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 2


@pytest.mark.django_db
def test_retrieve_qr_code_as_anonymous_user(default_client, qr_code):
    """
    An anonymous user should not be able to retrieve a QR Code.
    """

    response = default_client.get(f"{API_QR_CODE_BASE_URL}{qr_code.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_qr_code_as_member(member, api_client, qr_code):
    """
    A member of TIHLDE should be able to retrieve a QR Code owned by themself.
    """

    qr_code.user = member
    qr_code.save()

    client = api_client(user=member)
    response = client.get(f"{API_QR_CODE_BASE_URL}{qr_code.id}/")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_qr_code_as_another_member(member, api_client, qr_code):
    """
    A member of TIHLDE should not be able to retrieve a QR Code owned by another member.
    """

    client = api_client(user=member)
    response = client.get(f"{API_QR_CODE_BASE_URL}{qr_code.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("group_name", [AdminGroup.INDEX])
def test_retrieve_qr_code_as_index_member(member, qr_code, group_name):
    """
    A member of the index group should be able to retrieve a QR Code.
    """
    add_user_to_group_with_name(member, group_name)
    client = get_api_client(user=member)
    response = client.get(f"{API_QR_CODE_BASE_URL}{qr_code.id}/")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_qr_code_as_anonymous_user(default_client):
    """
    An anonymous user should not be able to create a QR Code.
    """

    data = get_data()
    response = default_client.post(API_QR_CODE_BASE_URL, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_qr_code_as_member(member, api_client):
    """
    A member of TIHLDE should be able to create a QR Code.
    """

    data = get_data()
    client = api_client(user=member)
    response = client.post(API_QR_CODE_BASE_URL, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_update_qr_code_as_anonymous_user(default_client, qr_code):
    """
    An anonymous user should not be able to update a QR Code.
    """

    data = get_data()
    response = default_client.put(f"{API_QR_CODE_BASE_URL}{qr_code.id}/", data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_qr_code_as_member(member, api_client, qr_code):
    """
    A member of TIHLDE should be able to update a QR Code owned by themself.
    """

    qr_code.user = member
    qr_code.save()

    data = get_data()
    client = api_client(user=member)
    response = client.put(f"{API_QR_CODE_BASE_URL}{qr_code.id}/", data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_qr_code_as_another_member(member, api_client, qr_code):
    """
    A member of TIHLDE should not be able to update a QR Code owned by another member.
    """

    data = get_data()
    client = api_client(user=member)
    response = client.put(f"{API_QR_CODE_BASE_URL}{qr_code.id}/", data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_destroy_qr_code_as_anonymous_user(default_client, qr_code):
    """
    An anonymous user should not be able to delete a QR Code.
    """

    response = default_client.delete(f"{API_QR_CODE_BASE_URL}{qr_code.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_destroy_qr_code_as_member(member, api_client, qr_code):
    """
    A member of TIHLDE should be able to delete a QR Code owned by themself.
    """

    qr_code.user = member
    qr_code.save()

    client = api_client(user=member)
    response = client.delete(f"{API_QR_CODE_BASE_URL}{qr_code.id}/")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_destroy_qr_code_as_another_member(member, api_client, qr_code):
    """
    A member of TIHLDE should not be able to delete a QR Code owned by another member.
    """

    client = api_client(user=member)
    response = client.delete(f"{API_QR_CODE_BASE_URL}{qr_code.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
