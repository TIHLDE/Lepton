from rest_framework import status

import pytest

from app.content.factories import LogEntryFactory
from app.util.test_utils import get_api_client

API_EVENTS_BASE_URL = "/log-entries/"


@pytest.mark.django_db
def test_logentry_list(admin_user):
    """
    An admin should be able to list log entries.
    """
    client = get_api_client(user=admin_user)
    response = client.get(API_EVENTS_BASE_URL)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_logentry_list_no_access(user):
    """
    An user should not be able to list log entries.
    """
    client = get_api_client(user=user)
    response = client.get(API_EVENTS_BASE_URL)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_logentry_retrieve(admin_user):
    """
    An admin should be able to retrieve a log entry.
    """
    log = LogEntryFactory()
    client = get_api_client(user=admin_user)
    response = client.get(f"{API_EVENTS_BASE_URL}{log.id}/")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_logentry_retrieve_no_access(user):
    """
    An user should not be able to retrieve a log entry.
    """
    log = LogEntryFactory()
    client = get_api_client(user=user)
    response = client.get(f"{API_EVENTS_BASE_URL}{log.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_logentry_create(admin_user):
    """
    An admin should not be able to create a log entry.
    """
    client = get_api_client(user=admin_user)
    response = client.post(API_EVENTS_BASE_URL, data={})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_logentry_update(admin_user):
    """
    An admin should not be able to update a log entry.
    """
    log = LogEntryFactory()
    client = get_api_client(user=admin_user)
    response = client.put(f"{API_EVENTS_BASE_URL}{log.id}/", data={})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_logentry_destroy(admin_user):
    """
    An admin should not be able to destroy a log entry.
    """
    log = LogEntryFactory()
    client = get_api_client(user=admin_user)
    response = client.delete(f"{API_EVENTS_BASE_URL}{log.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN
