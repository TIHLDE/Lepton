from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.content.factories.news_factory import NewsFactory
from app.content.factories.user_factory import UserFactory
from app.util.test_utils import get_api_client

API_NEWS_BASE_URL = "/api/v1/news/"


def _get_news_url():
    return API_NEWS_BASE_URL


def _get_news_detail_url(news):
    return f"{_get_news_url()}{news.id}/"


@pytest.fixture()
def news_post_data():
    return {
        "title": "test news",
        "header": "This is a test",
        "body": "body of test news",
    }


def _get_news_put_data(news):
    return {"title": news.title, "header": news.header, "body": news.body}


@pytest.mark.django_db
def test_news_ordering(default_client):
    """News should be ordered by date descending (newest first)."""
    oldest_news = NewsFactory()
    newest_news = NewsFactory()

    response = default_client.get(_get_news_url())
    response = response.json()

    assert response[0].get("title") == newest_news.title
    assert response[1].get("title") == oldest_news.title


@pytest.mark.django_db
def test_retrieve_when_not_found_returns_detail(default_client):
    """Should return a detail message in response."""
    news_not_found = NewsFactory.build()
    url = _get_news_detail_url(news_not_found)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail")


@pytest.mark.django_db
def test_retrieve_as_anonymous(default_client, news):
    """An anonymous user should be able to retrieve news."""
    url = _get_news_detail_url(news)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_as_member(member, news):
    """A member should be able to retrieve news."""
    url = _get_news_detail_url(news)
    client = get_api_client(user=member)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name", list(AdminGroup),
)
def test_retrieve_as_member_of_admin_group(member, news, group_name):
    """A member of an admin group should be able to retrieve news."""
    client = get_api_client(user=member, group_name=group_name)
    url = _get_news_detail_url(news)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_returns_news(default_client):
    """Should return all news."""
    NewsFactory()
    response = default_client.get(_get_news_url())

    assert len(response.json())


@pytest.mark.django_db
def test_list_as_anonymous_user(default_client):
    """An anonymous user should be able to list all news."""
    response = default_client.get(_get_news_url())

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_as_member(member):
    """A member should be able to list all news."""
    client = get_api_client(user=member)
    response = client.get(_get_news_url())

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name", list(AdminGroup),
)
def test_list_as_member_of_admin_group(member, group_name):
    """A member of an admin group should be able to list all news."""
    client = get_api_client(user=member, group_name=group_name)
    response = client.get(_get_news_url())

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_when_not_found():
    """Should return a detail message in response."""
    client = get_api_client(user=UserFactory(), group_name=AdminGroup.INDEX)
    news_not_found = NewsFactory.build()

    data = _get_news_put_data(news_not_found)
    url = _get_news_detail_url(news_not_found)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail")


@pytest.mark.django_db
def test_update_as_anonymous(default_client, news):
    """An anonymous user should not be able to update news."""
    data = _get_news_put_data(news)
    url = _get_news_detail_url(news)
    response = default_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_member(member, news):
    """A member should not be able to update news."""
    client = get_api_client(user=member)
    data = _get_news_put_data(news)
    url = _get_news_detail_url(news)
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
def test_update_as_member_of_admin_group(news, group_name, expected_status_code):
    """Only members of HS, Index or NoK should be able to update news."""
    client = get_api_client(user=UserFactory(), group_name=group_name)
    data = _get_news_put_data(news)
    url = _get_news_detail_url(news)
    response = client.put(url, data)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_update_returns_updated_news(news):
    """Should return the updated object in the response."""
    client = get_api_client(user=UserFactory(), group_name=AdminGroup.INDEX)

    news.title = "Updated title"
    data = _get_news_put_data(news)
    url = _get_news_detail_url(news)

    response = client.put(url, data)
    updated_title = response.json().get("title")

    assert updated_title == news.title


@pytest.mark.django_db
def test_create_as_anonymous(default_client, news_post_data):
    """An anonymous user should not be able to create news."""
    response = default_client.post(_get_news_url(), news_post_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_as_member(member, news_post_data):
    """A member should not be able to create news."""
    client = get_api_client(user=member)
    response = client.post(_get_news_url(), news_post_data)

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
    news_post_data, group_name, expected_status_code
):
    """Only members of HS, Index or NoK should be able to create news."""
    client = get_api_client(user=UserFactory(), group_name=group_name)
    response = client.post(_get_news_url(), news_post_data)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_destroy_when_not_found():
    """Should return a detail message in response."""
    client = get_api_client(user=UserFactory(), group_name=AdminGroup.INDEX)
    news_not_found = NewsFactory.build()

    url = _get_news_detail_url(news_not_found)
    response = client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail")


@pytest.mark.django_db
def test_destroy_as_anonymous(default_client, news):
    """An anonymous user should not be able to delete news."""
    url = _get_news_detail_url(news)
    response = default_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_destroy_as_member(member, news):
    """A member should not be able to delete news."""
    client = get_api_client(user=member)
    url = _get_news_detail_url(news)
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
def test_destroy_as_member_of_admin_group(news, group_name, expected_status_code):
    """Only members of HS, Index or NoK should be able to delete news."""
    client = get_api_client(user=UserFactory(), group_name=group_name)
    url = _get_news_detail_url(news)
    response = client.delete(url)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_destroy_returns_detail_in_response(news):
    """Should return a detail message in the response."""
    client = get_api_client(user=UserFactory(), group_name=AdminGroup.INDEX)
    url = _get_news_detail_url(news)
    response = client.delete(url)

    assert response.json().get("detail")
