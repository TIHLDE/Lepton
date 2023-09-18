from rest_framework import status

import pytest

from app.emoji.factories.toddel_emojis_factory import ToddelEmojisFactory
from app.util.test_utils import get_api_client

API_EMOJI_BASE_URL = "/emojis/"
API_TODDEL_EMOJIS_BASE_URL = f"{API_EMOJI_BASE_URL}toddelemojis/"


def _get_toddel_emojis_url():
    return f"{API_TODDEL_EMOJIS_BASE_URL}"


def _get_toddel_emojis_detailed_url(toddel_emojis):
    return f"{API_TODDEL_EMOJIS_BASE_URL}{toddel_emojis.id}/"


def _get_toddel_emojis_post_data(toddel, emojis_allowed):
    return {"toddel": toddel.edition, "emojis_allowed": emojis_allowed}


def _get_toddel_emojis_put_data(toddel_emojis):
    return {
        "toddel": toddel_emojis.toddel.edition,
        "emojis_allowed": True,
    }


@pytest.mark.django_db
def test_that_a_admin_can_allow_a_emoji_on_a_toddel(admin_user, toddel):
    """A admin should be able to allow emojis on a toddel"""

    url = _get_toddel_emojis_url()
    client = get_api_client(user=admin_user)
    data = _get_toddel_emojis_post_data(toddel, True)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_that_a_member_cannot_allow_emojis_on_a_toddel(member, toddel):
    """A member should not be able to allow emojis on a toddel"""

    url = _get_toddel_emojis_url()
    client = get_api_client(user=member)
    data = _get_toddel_emojis_post_data(toddel, True)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_that_a_nonmember_cannot_allow_emojis_on_a_toddel(user, toddel):
    """A nonmember should not be able to allow emojis on a toddel"""
    url = _get_toddel_emojis_url()
    client = get_api_client(user)
    data = _get_toddel_emojis_post_data(toddel, True)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_that_an_admin_can_change_emojis_allowence_on_a_toddel(admin_user):
    """An admin should be able to change the emojis allowence on a toddel"""

    toddel_emojis = ToddelEmojisFactory()

    url = _get_toddel_emojis_detailed_url(toddel_emojis)
    client = get_api_client(user=admin_user)
    data = _get_toddel_emojis_put_data(toddel_emojis)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_a_member_cannot_change_emojis_allowence_on_a_toddel(member):
    """a member should not be able to change the emojis allowence on a toddel"""

    toddel_emojis = ToddelEmojisFactory()

    url = _get_toddel_emojis_detailed_url(toddel_emojis)
    client = get_api_client(user=member)
    data = _get_toddel_emojis_put_data(toddel_emojis)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_that_a_nonmember_cannot_change_emojis_allowence_on_a_toddel(user):
    """a non member should not be able to change the emojis allowence on a toddel"""

    toddel_emojis = ToddelEmojisFactory()

    url = _get_toddel_emojis_detailed_url(toddel_emojis)
    client = get_api_client(user)
    data = _get_toddel_emojis_put_data(toddel_emojis)
    response = client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_that_an_admin_can_delete_emojis_allowence_on_a_toddel(admin_user):
    """An admin should be able to delete emojis allowence on a toddel"""

    url = _get_toddel_emojis_detailed_url(ToddelEmojisFactory())
    client = get_api_client(user=admin_user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_that_an_admin_can_not_delete_emojis_allowence_on_a_toddel(member):
    """A member should not be able to delete emojis allowence on a toddel"""

    url = _get_toddel_emojis_detailed_url(ToddelEmojisFactory())
    client = get_api_client(user=member)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
