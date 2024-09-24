from rest_framework import status

import pytest

from app.codex.enums import CodexGroups
from app.content.factories import MinuteFactory
from app.group.models import Group
from app.util.test_utils import add_user_to_group_with_name, get_api_client

API_MINUTE_BASE_URL = "/minutes/"


def get_minute_detail_url(minute):
    return f"{API_MINUTE_BASE_URL}{minute.id}/"


def get_minute_post_data(group=None):
    return {
        "title": "Test Minute",
        "content": "This is a test minute.",
        "group": group.slug if group else None,
    }


def get_minute_put_data(group=None):
    return {
        "title": "Test Minute update",
        "content": "This is a test minute update.",
        "group": group.slug if group else None,
    }


@pytest.mark.django_db
def test_create_minute_as_member(member):
    """A member should be not able to create a minute"""
    url = API_MINUTE_BASE_URL
    client = get_api_client(user=member)
    data = get_minute_post_data()
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_create_minute_as_codex_member(member, codex_group):
    """An index member should be able to create a minute"""
    url = API_MINUTE_BASE_URL
    add_user_to_group_with_name(member, codex_group)
    client = get_api_client(user=member)
    group = Group.objects.get(slug=codex_group)
    data = get_minute_post_data(group)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("codex_group", "swap"), (CodexGroups.all(), CodexGroups.reverse())
)
def test_create_to_another_group_as_codex_member(member, codex_group, swap):
    """A codex member should not be able to create a minute to another group"""
    add_user_to_group_with_name(member, codex_group)

    url = API_MINUTE_BASE_URL
    client = get_api_client(user=member)
    group = Group.objects.get_or_create(slug=swap, name=swap)[0]
    data = get_minute_post_data(group)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_minute_as_member(member, minute):
    """A member should not be able to update a minute"""
    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)
    index = Group.objects.get_or_create(slug="index", name="index")[0]
    data = get_minute_put_data(index)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("codex_group", "swap"), (CodexGroups.all(), CodexGroups.reverse())
)
def test_update_to_another_group_as_codex_member(member, minute, codex_group, swap):
    """A codex member should not be able to update a minute to another group"""
    add_user_to_group_with_name(member, codex_group)
    group = Group.objects.get(slug=codex_group)

    minute.author = member
    minute.group = group
    minute.save()

    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)

    swap_group = Group.objects.get_or_create(slug=swap, name=swap)[0]

    data = get_minute_put_data(swap_group)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_update_own_group_minute_as_codex_member(member, minute, codex_group):
    """A codex member should be able to update a minute that belongs to their group"""
    add_user_to_group_with_name(member, codex_group)
    group = Group.objects.get(slug=codex_group)

    minute.author = member
    minute.group = group
    minute.save()

    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)
    data = get_minute_put_data(group)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == data["title"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("codex_group", "swap"), (CodexGroups.all(), CodexGroups.reverse())
)
def test_update_another_group_minute_as_codex_member(member, minute, codex_group, swap):
    """A codex member should not be able to update a minute that belongs to another group"""
    add_user_to_group_with_name(member, codex_group)

    minute.group = Group.objects.get_or_create(slug=swap, name=swap)[0]
    minute.save()

    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)
    data = get_minute_put_data()
    response = client.put(url, data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_minute_as_member(member, minute):
    """A member should not be able to delete a minute"""
    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_delete_minute_as_codex_member(member, minute, codex_group):
    """A codex member should be able to delete a minute"""
    add_user_to_group_with_name(member, codex_group)

    minute.author = member
    minute.group = Group.objects.get(slug=codex_group)
    minute.save()

    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("codex_group", "swap"), (CodexGroups.all(), CodexGroups.reverse())
)
def test_delete_another_group_minute_as_codex_member(member, minute, codex_group, swap):
    """A codex member should not be able to delete a minute that belongs to another group"""
    add_user_to_group_with_name(member, codex_group)

    minute.group = Group.objects.get_or_create(slug=swap, name=swap)[0]
    minute.save()

    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_list_minutes_as_member(member):
    """A member should not be able to list minutes"""
    url = API_MINUTE_BASE_URL
    client = get_api_client(user=member)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_list_minutes_as_codex_member(member, codex_group):
    """A codex member should be able to list minutes from their own group"""
    add_user_to_group_with_name(member, codex_group)
    group = Group.objects.get(slug=codex_group)

    MinuteFactory.create_batch(5, group=group)
    MinuteFactory.create_batch(5)

    url = API_MINUTE_BASE_URL
    client = get_api_client(user=member)
    response = client.get(url)

    count = response.data["count"]
    results = response.data["results"]

    assert response.status_code == status.HTTP_200_OK
    assert count == 5
    assert all([minute["group"]["slug"] == codex_group.lower() for minute in results])


@pytest.mark.django_db
def test_retrieve_minute_as_member(member, minute):
    """A member should not be able to retrieve a minute"""
    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("codex_group", CodexGroups.all())
def test_retrieve_minute_as_codex_member(member, codex_group):
    """A codex member should be able to retrieve a minute from their own group"""
    add_user_to_group_with_name(member, codex_group)
    group = Group.objects.get(slug=codex_group)

    minute = MinuteFactory(group=group)

    url = get_minute_detail_url(minute)
    client = get_api_client(user=member)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["group"]["slug"] == codex_group.lower()
