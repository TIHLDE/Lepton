from random import randint

from rest_framework import status

import pytest

from app.career.factories import WeeklyBusinessFactory
from app.common.enums import AdminGroup
from app.content.factories.user_factory import UserFactory
from app.util import today
from app.util.test_utils import get_api_client

API_WEEKLY_BUSINESS_BASE_URL = "/api/v1/weekly-business/"


def _get_weekly_business_url():
    return API_WEEKLY_BUSINESS_BASE_URL


def _get_weekly_business_detail_url(weekly_business):
    return f"{_get_weekly_business_url()}{weekly_business.id}/"


@pytest.fixture()
def weekly_business_post_data():
    return {
        "image": "https://miro.medium.com/max/256/0*kFOfXBVPI_ZJvTa-.",
        "image_alt": "index_logo",
        "business_name": "Index",
        "body": "Lorem ipsum penum rektum benedikt gagge",
        "year": today().year,
        "week": randint(1, 52),
    }


def _get_weekly_business_put_data(weekly_business):
    return {
        "image": weekly_business.image,
        "image_alt": weekly_business.image_alt,
        "business_name": weekly_business.business_name,
        "body": weekly_business.body,
        "year": weekly_business.year,
        "week": weekly_business.week,
    }


@pytest.mark.django_db
def test_weekly_business_ordering(default_client):
    """weekly_business should be ordered by year then week"""
    oldest = WeeklyBusinessFactory(year=today().year + 1, week=2)
    middel = WeeklyBusinessFactory(year=today().year + 1, week=10)
    newest = WeeklyBusinessFactory(year=today().year + 2, week=4)

    response = default_client.get(_get_weekly_business_url())
    response = response.json()

    assert response["results"][0].get("business_name") == oldest.business_name
    assert response["results"][1].get("business_name") == middel.business_name
    assert response["results"][2].get("business_name") == newest.business_name


@pytest.mark.django_db
def test_retrieve_when_not_found_returns_detail(default_client):
    """Should return a detail message in response."""
    weekly_business_not_found = WeeklyBusinessFactory.build()
    url = _get_weekly_business_detail_url(weekly_business_not_found)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail")


@pytest.mark.django_db
def test_retrieve_as_anonymous(default_client, weekly_business):
    """An anonymous user should be able to retrieve weekly_business."""
    url = _get_weekly_business_detail_url(weekly_business)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_as_member(member, weekly_business):
    """A member should be able to retrieve weekly_business."""
    url = _get_weekly_business_detail_url(weekly_business)
    client = get_api_client(user=member)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name", list(AdminGroup),
)
def test_retrieve_as_member_of_admin_group(member, weekly_business, group_name):
    """A member of an admin group should be able to retrieve weekly_business."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_weekly_business_detail_url(weekly_business)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_returns_weekly_business(default_client):
    """Should return all weekly_business."""
    WeeklyBusinessFactory()
    response = default_client.get(_get_weekly_business_url())

    assert len(response.json())


@pytest.mark.django_db
def test_list_as_anonymous_user(default_client):
    """An anonymous user should be able to list all weekly_business."""
    response = default_client.get(_get_weekly_business_url())

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_as_member(member):
    """A member should be able to list all weekly_business."""
    client = get_api_client(user=member)
    response = client.get(_get_weekly_business_url())

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name", list(AdminGroup),
)
def test_list_as_member_of_admin_group(member, group_name):
    """A member of an admin group should be able to list all weekly_business."""
    client = get_api_client(user=member, group_name=group_name)
    response = client.get(_get_weekly_business_url())

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_when_not_found():
    """Should return a detail message in response."""
    client = get_api_client(user=UserFactory(), group_name=AdminGroup.INDEX)
    weekly_business_not_found = WeeklyBusinessFactory.build()

    data = _get_weekly_business_put_data(weekly_business_not_found)
    url = _get_weekly_business_detail_url(weekly_business_not_found)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail")


@pytest.mark.django_db
def test_update_as_anonymous(default_client, weekly_business):
    """An anonymous user should not be able to update weekly_business."""
    data = _get_weekly_business_put_data(weekly_business)
    url = _get_weekly_business_detail_url(weekly_business)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_member(member, weekly_business):
    """A member should not be able to update weekly_business."""
    client = get_api_client(user=member)
    data = _get_weekly_business_put_data(weekly_business)
    url = _get_weekly_business_detail_url(weekly_business)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_200_OK),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
    ],
)
def test_update_as_member_of_admin_group(
    weekly_business, group_name, expected_status_code
):
    """Only members of HS, Index or NoK should be able to update weekly_business."""
    client = get_api_client(user=UserFactory(), group_name=group_name)
    data = _get_weekly_business_put_data(weekly_business)
    url = _get_weekly_business_detail_url(weekly_business)
    response = client.put(url, data)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_update_returns_updated_weekly_business(weekly_business):
    """Should return the updated object in the response."""
    client = get_api_client(user=UserFactory(), group_name=AdminGroup.INDEX)

    weekly_business.business_name = "Updated business_name"
    data = _get_weekly_business_put_data(weekly_business)
    url = _get_weekly_business_detail_url(weekly_business)

    response = client.put(url, data)
    updated_title = response.json().get("business_name")

    assert updated_title == weekly_business.business_name


@pytest.mark.django_db
def test_create_as_anonymous(default_client, weekly_business_post_data):
    """An anonymous user should not be able to create weekly_business."""
    response = default_client.post(
        _get_weekly_business_url(), weekly_business_post_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_as_member(member, weekly_business_post_data):
    """A member should not be able to create weekly_business."""
    client = get_api_client(user=member)
    response = client.post(_get_weekly_business_url(), weekly_business_post_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_201_CREATED),
        (AdminGroup.INDEX, status.HTTP_201_CREATED),
        (AdminGroup.NOK, status.HTTP_201_CREATED),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_as_member_of_admin_group(
    weekly_business_post_data, group_name, expected_status_code
):
    """Only members of HS, Index or NoK should be able to create weekly_business."""
    client = get_api_client(user=UserFactory(), group_name=group_name)
    response = client.post(_get_weekly_business_url(), weekly_business_post_data)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_destroy_when_not_found():
    """Should return a detail message in response."""
    client = get_api_client(user=UserFactory(), group_name=AdminGroup.INDEX)
    weekly_business_not_found = WeeklyBusinessFactory.build()

    url = _get_weekly_business_detail_url(weekly_business_not_found)
    response = client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail")


@pytest.mark.django_db
def test_destroy_as_anonymous(default_client, weekly_business):
    """An anonymous user should not be able to delete weekly_business."""
    url = _get_weekly_business_detail_url(weekly_business)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_destroy_as_member(member, weekly_business):
    """A member should not be able to delete weekly_business."""
    client = get_api_client(user=member)
    url = _get_weekly_business_detail_url(weekly_business)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_200_OK),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
    ],
)
def test_destroy_as_member_of_admin_group(
    weekly_business, group_name, expected_status_code
):
    """Only members of HS, Index or NoK should be able to delete weekly_business."""
    client = get_api_client(user=UserFactory(), group_name=group_name)
    url = _get_weekly_business_detail_url(weekly_business)
    response = client.delete(url)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_destroy_returns_detail_in_response(weekly_business):
    """Should return a detail message in the response."""
    client = get_api_client(user=UserFactory(), group_name=AdminGroup.INDEX)
    url = _get_weekly_business_detail_url(weekly_business)
    response = client.delete(url)

    assert response.json().get("detail")
