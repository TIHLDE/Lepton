from rest_framework import status

import pytest

from app.common.enums import AdminGroup, Groups
from app.common.enums import NativeGroupType as GroupType
from app.common.enums import NativeMembershipType as MembershipType
from app.content.factories.news_factory import NewsFactory
from app.content.factories.user_factory import UserFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client

API_NEWS_BASE_URL = "/news/"


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

    assert response["results"][0].get("title") == newest_news.title
    assert response["results"][1].get("title") == oldest_news.title


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
    "group_name",
    list(AdminGroup),
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
    "group_name",
    list(AdminGroup),
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
        (AdminGroup.SOSIALEN, status.HTTP_200_OK),
        (AdminGroup.PROMO, status.HTTP_200_OK),
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
        (AdminGroup.SOSIALEN, status.HTTP_201_CREATED),
        (AdminGroup.PROMO, status.HTTP_201_CREATED),
        (Groups.FONDET, status.HTTP_201_CREATED),
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
def test_create_with_creator(news_post_data, member):
    """When creating news, one should be able to set a creator"""
    client = get_api_client(user=UserFactory(), group_name=AdminGroup.PROMO)
    data = news_post_data
    data["creator"] = member.user_id
    response = client.post(_get_news_url(), data)

    assert response.json()["creator"]["user_id"] == member.user_id
    assert response.status_code == status.HTTP_201_CREATED


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
        (AdminGroup.SOSIALEN, status.HTTP_200_OK),
        (AdminGroup.PROMO, status.HTTP_200_OK),
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


@pytest.mark.django_db
def test_create_news_as_leader_of_committee(member):
    """A leader of a committee should be able to create news."""
    add_user_to_group_with_name(
        member,
        "Committee",
        group_type=GroupType.COMMITTEE,
        membership_type=MembershipType.LEADER,
    )
    client = get_api_client(user=member)
    response = client.post(
        _get_news_url(), {"title": "title", "header": "header", "body": "body"}
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("field", "value", "expected_status_code", "expected_count"),
    [
        ("title", "title1", status.HTTP_200_OK, 1),
        ("search", "title", status.HTTP_200_OK, 3),
        ("search", "ne", status.HTTP_200_OK, 1),
        ("search", "body", status.HTTP_200_OK, 4),
        ("search", "header", status.HTTP_200_OK, 4),
        ("search", "News", status.HTTP_200_OK, 1),
        ("search", "header1", status.HTTP_200_OK, 1),
    ],
)
def test_news_filter_works_as_expected(
    member, field, value, expected_status_code, expected_count
):
    """A leader of a committee should be able to create news."""

    news1 = NewsFactory(title="title1", header="header1", body="body1")
    news2 = NewsFactory(title="title2", header="header2", body="body2")
    news3 = NewsFactory(title="title3", header="header3", body="body3")
    news4 = NewsFactory(title="News", header="header4", body="body4")

    client = get_api_client(user=member)

    url = _get_news_url() + "?" + field + "=" + value
    response = client.get(url)

    assert response.data["count"] == expected_count
    assert response.status_code == expected_status_code
