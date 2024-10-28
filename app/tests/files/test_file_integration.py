from io import BytesIO

import pytest
from pycodestyle import readlines
from rest_framework import status

from app.common.enums import AdminGroup, Groups
from app.files.models.file import File
from app.files.models.user_gallery import UserGallery
from app.util.test_utils import (
    add_user_to_group_with_name,
    get_api_client,
    remove_user_from_group_with_name,
)
from app.constants import MAX_GALLERY_SIZE

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


def _create_file(user, gallery=None):
    """Helper function to create a file in the database."""
    if gallery is None:
        gallery, _ = UserGallery.objects.get_or_create(author=user)

    return File.objects.create(
        title="Sample File",
        url="https://example.com/file.pdf",
        description="This is a sample file.",
        gallery=gallery,
    )


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


@pytest.mark.django_db
def test_create_file_as_member(member):
    """Tests if a member can create a file"""
    client = get_api_client(user=member)
    url = _get_file_url()
    data = _get_file_post_data()

    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_file_as_admin(admin_user, admin_gallery):
    """Tests if an admin can create a file"""
    client = get_api_client(user=admin_user)
    url = _get_file_url()
    data = _get_file_post_data()

    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert File.objects.filter(title=data["title"]).exists()
    file = File.objects.get(title=data["title"])
    assert file.gallery == admin_gallery


@pytest.mark.django_db
def test_create_file_gallery_full(admin_user, admin_gallery):
    """Tests if the admin cannot create a file when gallery is full (>=50 files)"""
    for _ in range(MAX_GALLERY_SIZE):
        _create_file(admin_user, admin_gallery)

    client = get_api_client(user=admin_user)
    url = _get_file_url()
    data = _get_file_post_data()

    response = client.post(url, data)

    print(response.data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# noinspection PyTypeChecker
@pytest.mark.django_db
def test_retrieve_file_does_not_exist(admin_user):
    """Tests retrieving a non-existent file"""
    client = get_api_client(user=admin_user)
    url = _get_file_url(file=None) + "999/"

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "Ikke funnet."


@pytest.mark.django_db
def test_delete_file_as_admin(admin_user, admin_gallery):
    """Tests if an admin user can delete their file"""
    file = _create_file(admin_user, admin_gallery)

    client = get_api_client(user=admin_user)
    url = _get_file_url(file)

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not File.objects.filter(id=file.id).exists()


@pytest.mark.django_db
def test_delete_file_as_non_author(member, new_admin_user):
    """Tests if a non-author cannot delete another user's file"""
    add_user_to_group_with_name(member, AdminGroup.HS)

    admin_gallery = UserGallery.objects.create(author=new_admin_user)

    file = _create_file(new_admin_user, admin_gallery)

    client = get_api_client(user=member)
    url = _get_file_url(file)

    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert File.objects.filter(id=file.id).exists()


@pytest.mark.django_db
def test_update_file_as_admin_with_file(admin_user, admin_gallery):
    """Tests if an admin can update a file with a new file successfully."""
    file = _create_file(admin_user, admin_gallery)
    client = get_api_client(user=admin_user)
    url = _get_file_url(file)

    file_content = BytesIO(b"This is a test file content.")
    file_content.name = "updated_file.pdf"

    data = {
        "title": "Updated Sample File",
        "url": "https://example.com/updated_file.pdf",
        "description": "This is an updated sample file.",
        "file": file_content,
    }

    response = client.put(url, data, format="multipart")

    assert response.status_code == status.HTTP_200_OK
    file.refresh_from_db()
    assert file.title == "Updated Sample File"
    assert file.url == "https://example.com/updated_file.pdf"
    assert file.description == "This is an updated sample file."


@pytest.mark.django_db
def test_update_file_as_admin_without_file(admin_user, admin_gallery):
    """Tests if an admin can update a file without providing a new file."""
    file = _create_file(admin_user, admin_gallery)
    client = get_api_client(user=admin_user)
    url = _get_file_url(file)

    data = {
        "title": "Updated Sample File",
        "url": "https://example.com/updated_file.pdf",
        "description": "This is an updated sample file.",
    }

    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    file.refresh_from_db()
    assert file.title == "Updated Sample File"
    assert file.url == "https://example.com/updated_file.pdf"
    assert file.description == "This is an updated sample file."


@pytest.mark.django_db
def test_update_file_as_member(member, user_gallery):
    """Tests if a member cannot update a file."""
    file = _create_file(member, user_gallery)
    client = get_api_client(user=member)
    url = _get_file_url(file)

    data = {
        "title": "Attempted Update by Member",
    }

    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_file_invalid_data(admin_user, admin_gallery):
    """Tests if an admin cannot update a file with invalid data."""
    file = _create_file(admin_user, admin_gallery)
    client = get_api_client(user=admin_user)
    url = _get_file_url(file)

    data = {
        "title": "",
    }

    response = client.put(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "title" in response.data


@pytest.mark.django_db
def test_update_non_existent_file(admin_user):
    """Tests if an admin cannot update a non-existent file."""
    client = get_api_client(user=admin_user)
    url = _get_file_url() + "999/"

    data = {
        "title": "Non-Existent File",
    }

    response = client.put(url, data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_partial_update_file(admin_user, admin_gallery):
    """Tests if an admin can partially update a file."""
    file = _create_file(admin_user, admin_gallery)
    client = get_api_client(user=admin_user)
    url = _get_file_url(file)

    data = {
        "description": "This is a partially updated description.",
    }

    response = client.patch(url, data)

    assert response.status_code == status.HTTP_200_OK
    file.refresh_from_db()
    assert file.description == "This is a partially updated description."


@pytest.mark.django_db
def test_update_file_with_new_file(admin_user, admin_gallery):
    """Tests if an admin can update a file with a new file URL."""
    file = _create_file(admin_user, admin_gallery)
    client = get_api_client(user=admin_user)
    url = _get_file_url(file)

    data = {
        "url": "https://example.com/newfile.pdf",
    }

    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    file.refresh_from_db()
    assert file.url == "https://example.com/newfile.pdf"


@pytest.mark.django_db
def test_create_file_as_admin_and_delete_as_tihlde_user(admin_user, admin_gallery):
    """Tests if an admin can create a file and delete it after being removed as an admin."""
    file = _create_file(admin_user, admin_gallery)
    url = _get_file_url(file)

    remove_user_from_group_with_name(admin_user, AdminGroup.HS)
    add_user_to_group_with_name(admin_user, Groups.TIHLDE)

    client = get_api_client(user=admin_user)

    delete_response = client.delete(url)

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
