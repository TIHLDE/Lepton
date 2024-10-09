from rest_framework import status

import pytest

from app.util.test_utils import get_api_client

FILE_URL = "/files/file/"


def _get_file_url(file=None):
    return f"{FILE_URL}{file.id}/" if file else f"{FILE_URL}"


def _get_file_post_data():
    return {
        "title": "Sample File",
        "url": "https://example.com/file.pdf",
        "description": "This is a sample file.",
    }


def _get_file_put_data(file):
    return {"title": file.title, "url": file.url, "description": "Updated description."}


@pytest.mark.django_db
def test_list_files_as_anonymous_user(default_client):
    """Tests if an anonymous user cannot list files"""
    url = _get_file_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_files_as_member(member):
    """Tests if a member can list files"""
    client = get_api_client(user=member)
    url = _get_file_url()
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_files_as_admin(admin_user):
    """Tests if an admin user can list files"""
    client = get_api_client(user=admin_user)
    url = _get_file_url()
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
