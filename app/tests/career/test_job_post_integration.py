from rest_framework import status

import pytest

from app.common.permissions import AdminGroup
from app.content.factories import QRCodeFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client

API_QR_CODE_BASE_URL = "/jobposts/"


def get_data():
    return {
        "title": "Test Job Post",
        "ingress": "Test Ingress",
        "body": "Test Body",
        "location": "Test Location",
        "deadline": "2021-12-12T12:00:00Z",
        "company": "Test Company",
        "email": "test_company@test.com",
    }


@pytest.mark.django_db
def test_list_job_posts_as_anonymous_user(default_client):
    """
    An anonymous user should be able to list job posts.
    """

    response = default_client.get(API_QR_CODE_BASE_URL)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_job_posts_as_member(member, api_client):
    """
    A member of TIHLDE should be able to list job posts.
    """

    client = api_client(user=member)
    response = client.get(API_QR_CODE_BASE_URL)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_job_post_as_anonymous_user(default_client, job_post):
    """
    An anonymous user should be able to retrieve a job post.
    """

    response = default_client.get(f"{API_QR_CODE_BASE_URL}{job_post.id}/")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_job_post_as_member(member, api_client, job_post):
    """
    A member of TIHLDE should be able to retrieve a job post.
    """

    client = api_client(user=member)
    response = client.get(f"{API_QR_CODE_BASE_URL}{job_post.id}/")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_job_post_as_anonymous_user(default_client):
    """
    An anonymous user should not be able to create a job post.
    """

    response = default_client.post(API_QR_CODE_BASE_URL, data=get_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_job_post_as_member(member, api_client):
    """
    A member of TIHLDE should not be able to create a job post.
    """

    client = api_client(user=member)
    response = client.post(API_QR_CODE_BASE_URL, data=get_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("group", [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK])
def test_create_job_post_as_admin(member, group):
    """
    A member of the admin group should be able to create a job post.
    """

    add_user_to_group_with_name(member, group)
    client = get_api_client(user=member)
    response = client.post(API_QR_CODE_BASE_URL, data=get_data())

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_update_job_post_as_anonymous_user(default_client, job_post):
    """
    An anonymous user should not be able to update a job post.
    """

    response = default_client.put(
        f"{API_QR_CODE_BASE_URL}{job_post.id}/", data=get_data()
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_job_post_as_member(member, api_client, job_post):
    """
    A member of TIHLDE should not be able to update a job post.
    """

    client = api_client(user=member)
    response = client.put(f"{API_QR_CODE_BASE_URL}{job_post.id}/", data=get_data())

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("group", [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK])
def test_update_job_post_as_admin(member, group, job_post):
    """
    A member of the admin group should be able to update a job post.
    """

    add_user_to_group_with_name(member, group)
    client = get_api_client(user=member)
    response = client.put(f"{API_QR_CODE_BASE_URL}{job_post.id}/", data=get_data())

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_destroy_job_post_as_anonymous_user(default_client, job_post):
    """
    An anonymous user should not be able to destroy a job post.
    """

    response = default_client.delete(f"{API_QR_CODE_BASE_URL}{job_post.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_destroy_job_post_as_member(member, api_client, job_post):
    """
    A member of TIHLDE should not be able to destroy a job post.
    """

    client = api_client(user=member)
    response = client.delete(f"{API_QR_CODE_BASE_URL}{job_post.id}/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("group", [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK])
def test_destroy_job_post_as_admin(member, group, job_post):
    """
    A member of the admin group should be able to destroy a job post.
    """

    add_user_to_group_with_name(member, group)
    client = get_api_client(user=member)
    response = client.delete(f"{API_QR_CODE_BASE_URL}{job_post.id}/")

    assert response.status_code == status.HTTP_200_OK
