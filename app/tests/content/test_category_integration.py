import pytest

from rest_framework import status

from app.util.test_utils import get_api_client


API_CATEGORY_BASE_URL = "/categories/"


def get_category_data():
    return {
        "text": "test"
    }


@pytest.mark.django_db
def test_list_categories_as_anonymous_user(default_client):
    """An anonymous user should not be able to list all categories"""
    response = default_client.get(API_CATEGORY_BASE_URL)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_categories_as_member(member):
    """
    A member of TIHLDE should be able to list all categories.
    """
    client = get_api_client(user=member)
    response = client.get(API_CATEGORY_BASE_URL)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_category_as_anonymous_user(default_client, category):
    """An anonymous user should not be able to retrieve a category entity."""
    response = default_client.get(f"{API_CATEGORY_BASE_URL}{category.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_category_as_member(member, category):
    """
    A member of TIHLDE should be able to retrieve a category entity.
    """
    client = get_api_client(user=member)
    response = client.get(f"{API_CATEGORY_BASE_URL}{category.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == category.id


@pytest.mark.django_db
def test_create_category_as_anonymous_user(default_client):
    """An anonymous user should not be able to create a category entity."""
    response = default_client.post(API_CATEGORY_BASE_URL, get_category_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_category_as_member(member):
    """
    A member of TIHLDE should not be able to create a category entity.
    """
    client = get_api_client(user=member)
    response = client.post(API_CATEGORY_BASE_URL, get_category_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_category_as_admin(admin_user):
    """
    An admin user should be able to create a category entity.
    """
    client = get_api_client(user=admin_user)
    response = client.post(API_CATEGORY_BASE_URL, get_category_data())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["text"] == get_category_data()["text"]


@pytest.mark.django_db
def test_update_category_as_anonymous_user(default_client, category):
    """An anonymous user should not be able to update a category entity."""
    response = default_client.put(f"{API_CATEGORY_BASE_URL}{category.id}/", get_category_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_category_as_member(member, category):
    """
    A member of TIHLDE should not be able to update a category entity.
    """
    client = get_api_client(user=member)
    response = client.put(f"{API_CATEGORY_BASE_URL}{category.id}/", get_category_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_category_as_admin(admin_user, category):
    """
    An admin user should be able to update a category entity.
    """
    client = get_api_client(user=admin_user)
    response = client.put(f"{API_CATEGORY_BASE_URL}{category.id}/", get_category_data())

    assert response.status_code == status.HTTP_200_OK
    assert response.data["text"] == get_category_data()["text"]


@pytest.mark.django_db
def test_delete_category_as_anonymous_user(default_client, category):
    """An anonymous user should not be able to delete a category entity."""
    response = default_client.delete(f"{API_CATEGORY_BASE_URL}{category.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_category_as_member(member, category):
    """
    A member of TIHLDE should not be able to delete a category entity.
    """
    client = get_api_client(user=member)
    response = client.delete(f"{API_CATEGORY_BASE_URL}{category.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_category_as_admin(admin_user, category):
    """
    An admin user should be able to delete a category entity.
    """
    client = get_api_client(user=admin_user)
    response = client.delete(f"{API_CATEGORY_BASE_URL}{category.id}/")

    assert response.status_code == status.HTTP_200_OK