from rest_framework import status

import pytest

from app.util.test_utils import get_api_client

API_MINUTE_BASE_URL = "/minutes/"


def get_minute_detail_url(minute):
    return f"{API_MINUTE_BASE_URL}{minute.id}/"


def get_minute_post_data():
    return {"title": "Test Minute", "content": "This is a test minute."}


def get_minute_put_data():
    return {"title": "Test Minute update", "content": "This is a test minute update."}


@pytest.mark.django_db
def test_create_minute_as_member(member):
    """A member should be not able to create a minute"""
    url = API_MINUTE_BASE_URL
    client = get_api_client(user=member)
    data = get_minute_post_data()
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_minute_as_index_member(index_member):
    """An index member should be able to create a minute"""
    url = API_MINUTE_BASE_URL
    client = get_api_client(user=index_member)
    data = get_minute_post_data()
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_update_minute_as_member(member, minute):
    """A member should not be able to update a minute"""
    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)
    data = get_minute_put_data()
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_minute_as_index_member(index_member, minute):
    """An index member should be able to update a minute"""
    minute.author = index_member
    minute.save()
    url = get_minute_detail_url(minute)
    client = get_api_client(user=index_member)
    data = get_minute_put_data()
    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == data["title"]


@pytest.mark.django_db
def test_delete_minute_as_member(member, minute):
    """A member should not be able to delete a minute"""
    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_minute_as_index_member(index_member, minute):
    """An index member should be able to delete a minute"""
    minute.author = index_member
    minute.save()
    url = get_minute_detail_url(minute)
    client = get_api_client(user=index_member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_minutes_as_member(member):
    """A member should not be able to list minutes"""
    url = API_MINUTE_BASE_URL
    client = get_api_client(user=member)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_minutes_as_index_member(index_member, minute):
    """An index member should be able to list minutes"""
    minute.author = index_member
    minute.save()
    url = API_MINUTE_BASE_URL
    client = get_api_client(user=index_member)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_minute_as_member(member, minute):
    """A member should not be able to retrieve a minute"""
    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_minute_as_index_member(index_member, minute):
    """An index member should be able to retrieve a minute"""
    minute.author = index_member
    minute.save()
    url = get_minute_detail_url(minute)
    client = get_api_client(user=index_member)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == minute.id
