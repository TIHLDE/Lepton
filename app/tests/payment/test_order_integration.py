from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.payment.enums import OrderStatus
from app.util.test_utils import add_user_to_group_with_name, get_api_client

API_ORDERS_BASE_URL = "/payments/"


def get_orders_url_detail(order_id):
    return f"{API_ORDERS_BASE_URL}{order_id}/"


@pytest.mark.django_db
def test_list_orders_as_anonymous_user(default_client):
    """An anonymous user should not be able to list orders."""
    response = default_client.get(API_ORDERS_BASE_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_orders_as_user(member):
    """A user should not be able to list orders."""
    client = get_api_client(user=member)
    response = client.get(API_ORDERS_BASE_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("group_name", AdminGroup.all())
def test_list_orders_as_admin_user(member, group_name):
    """A member of an admin group should be able to list orders."""
    add_user_to_group_with_name(member, group_name)
    client = get_api_client(user=member)
    response = client.get(API_ORDERS_BASE_URL)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_order_as_anonymous_user(default_client, order):
    """An anonymous user should not be able to retrieve an order."""
    response = default_client.get(get_orders_url_detail(order.order_id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_order_as_member(member, order):
    """A user should not be able to retrieve an order."""
    client = get_api_client(user=member)
    response = client.get(get_orders_url_detail(order.order_id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("group_name", AdminGroup.all())
def test_retrieve_order_as_admin_user(member, order, group_name):
    """A member of an adming group should be able to retrieve an order."""
    add_user_to_group_with_name(member, group_name)
    client = get_api_client(user=member)
    response = client.get(get_orders_url_detail(order.order_id))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_order_as_anonymous_user(default_client, order):
    """An anonymous user should not be able to delete an order."""
    response = default_client.delete(get_orders_url_detail(order.order_id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_order_as_member(member, order):
    """A user should not be able to delete an order."""
    client = get_api_client(user=member)
    response = client.delete(get_orders_url_detail(order.order_id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("group_name", [AdminGroup.INDEX])
def test_delete_order_as_index_user(member, order, group_name):
    """An index user should be able to delete an order."""
    add_user_to_group_with_name(member, group_name)
    client = get_api_client(user=member)
    response = client.delete(get_orders_url_detail(order.order_id))
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_update_order_as_anonymous_user(default_client, order):
    """An anonymous user should not be able to update an order."""
    response = default_client.put(get_orders_url_detail(order.order_id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_order_as_member(member, order):
    """A user should not be able to update an order."""
    client = get_api_client(user=member)
    response = client.put(get_orders_url_detail(order.order_id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("group_name", [*AdminGroup.admin()])
def test_update_order_as_admin_user(member, order, group_name):
    """An index and HS user should be able to update an order."""
    add_user_to_group_with_name(member, group_name)
    client = get_api_client(user=member)
    data = {"status": OrderStatus.SALE}
    response = client.put(get_orders_url_detail(order.order_id), data=data)
    assert response.status_code == status.HTTP_200_OK

    order.refresh_from_db()

    assert order.status == OrderStatus.SALE
