from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.content.factories.page_factory import PageFactory
from app.util.test_utils import get_api_client

PAGE_URL = "/api/v1/page/"


def _get_page_url(page=None):
    return f"{PAGE_URL}{page.get_path()}" if (page) else f"{PAGE_URL}"


def _get_page_post_data(page):
    return {
        "slug": page.slug,
        "title": page.title,
        "path": page.parent.get_path(),
    }


def _get_page_put_data(page):
    return {**_get_page_post_data(page), "content": "Awesome content :"}


@pytest.mark.django_db
def test_list_returns_root_as_anonymous_user(default_client, page):
    """Tests if an anonymous user can list pages and receive the root page"""

    url = _get_page_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["slug"] == page.parent.slug


@pytest.mark.django_db
def test_retrieve_page_as_anonymous_user(default_client, page):
    """Tests if an anonymous user can retrieve a page"""
    url = _get_page_url(page)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["path"] == page.get_path()


@pytest.mark.django_db
def test_retrieve_as_user(page, user):
    """Tests if a logged in user can retrieve a page"""

    url = _get_page_url(page)
    client = get_api_client(user=user)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["path"] == page.get_path()


@pytest.mark.django_db
def test_update_as_anonymous_user(default_client, page):
    """Tests if an anonymous user fails to update a page"""

    url = _get_page_url(page)
    response = default_client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_user(page, user):
    """Tests if a logged in user fails to update a page"""

    client = get_api_client(user=user)
    url = _get_page_url(page)
    response = client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code", "new_content"),
    [
        (AdminGroup.HS, status.HTTP_200_OK, "Awesome content :"),
        (AdminGroup.INDEX, status.HTTP_200_OK, "Awesome content :"),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN, None),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN, None),
        ("Non_admin_group", status.HTTP_403_FORBIDDEN, None),
    ],
)
def test_update_as_group_user(
    page, user, group_name, expected_status_code, new_content,
):
    """Tests different groups ability to update a page"""
    expected_content = new_content if new_content else page.content

    client = get_api_client(user=user, group_name=group_name)
    url = _get_page_url(page)
    data = _get_page_put_data(page=page)
    response = client.put(url, data=data)
    page.refresh_from_db()

    assert response.status_code == expected_status_code
    assert page.content == expected_content


@pytest.mark.django_db
def test_change_parent_page_of_a_page(admin_user, parent_page):
    """Tests moving a page to another place in the tree"""
    page1 = PageFactory(parent=parent_page)
    page2 = PageFactory(parent=parent_page)
    client = get_api_client(user=admin_user)
    url = _get_page_url(page1)
    data = _get_page_put_data(page=page1)
    data["path"] = page2.get_path()
    response = client.put(url, data=data)
    page1.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert page1.parent.page_id == page2.page_id
    assert response.json()["path"] == page2.get_path() + response.json()["slug"] + "/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        ("Non_admin_group", status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_as_group_user(page, user, group_name, expected_status_code):
    """Tests different groups ability to create a page"""

    client = get_api_client(user=user, group_name=group_name)
    url = _get_page_url()
    data = _get_page_post_data(page=page)
    data["title"] = "New page"
    response = client.post(url, data=data)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        ("Non_admin_group", status.HTTP_403_FORBIDDEN),
    ],
)
def test_delete_as_group_user(page, user, group_name, expected_status_code):
    """Tests if different groups ability to delete a page"""

    client = get_api_client(user=user, group_name=group_name)
    url = _get_page_url(page)
    response = client.delete(url)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_delete_cannot_delete_page_with_children(parent_page, admin_user):
    """Tests that you cannot delete a page that has subpages"""

    page1 = PageFactory(parent=parent_page)
    PageFactory(parent=page1)
    client = get_api_client(user=admin_user)
    url = _get_page_url(page1)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_as_group_user_fails_when_no_root_exists(admin_user):
    """Tests that you cannot create a root page"""

    client = get_api_client(user=admin_user)
    url = _get_page_url()
    data = {"title": "new page", "path": ""}
    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
