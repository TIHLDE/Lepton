from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.group.factories import GroupFactory
from app.group.models import Group
from app.payment.enums import OrderStatus
from app.payment.factories import OrderFactory
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
@pytest.mark.parametrize("group_name", AdminGroup.admin())
def test_list_orders_as_admin_user(member, group_name):
    """An admin or index user should be able to list orders."""
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
def test_retrieve_own_order_as_member(member, order):
    """A user should be able to retrieve their own order."""
    order.user = member
    order.save()
    client = get_api_client(user=member)
    response = client.get(get_orders_url_detail(order.order_id))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize("group_name", AdminGroup.admin())
def test_retrieve_order_as_admin_user(member, order, group_name):
    """An admin or member of Index should be able to retrieve an order."""
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
    """An index user should not be able to delete an order."""
    add_user_to_group_with_name(member, group_name)
    client = get_api_client(user=member)
    response = client.delete(get_orders_url_detail(order.order_id))
    assert response.status_code == status.HTTP_403_FORBIDDEN


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
@pytest.mark.parametrize("group_name", [AdminGroup.INDEX])
def test_update_order_as_index_user(member, order, group_name):
    """An index user should be able to update an order."""
    add_user_to_group_with_name(member, group_name)
    client = get_api_client(user=member)
    data = {"status": OrderStatus.SALE}
    response = client.put(get_orders_url_detail(order.order_id), data=data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name", [AdminGroup.HS, AdminGroup.KOK, AdminGroup.SOSIALEN]
)
def test_update_order_as_admin_user(member, order, group_name):
    """Members of admin groups other than index should not be able to update an order."""
    add_user_to_group_with_name(member, group_name)
    client = get_api_client(user=member)
    data = {"status": OrderStatus.SALE}
    response = client.put(get_orders_url_detail(order.order_id), data=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_order_as_organizer(member, event, order):
    """Test that members of the organizing group (e.g., SOSIALEN) can update an order."""
    organizer_group = GroupFactory(name=AdminGroup.SOSIALEN)
    add_user_to_group_with_name(member, organizer_group.name)

    event.organizer = organizer_group
    event.save()

    order.event = event
    order.save()

    data = {"status": OrderStatus.SALE}
    client = get_api_client(user=member)

    response = client.put(get_orders_url_detail(order.order_id), data=data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_order_as_non_organizer(member, event, order):
    """Test that members not in the organizing group do not have permission to update an order."""
    organizer_group = GroupFactory(name=AdminGroup.SOSIALEN)
    add_user_to_group_with_name(member, AdminGroup.NOK)

    event.organizer = organizer_group
    event.save()

    order.event = event
    order.save()

    data = {"status": OrderStatus.SALE}
    client = get_api_client(user=member)

    response = client.put(get_orders_url_detail(order.order_id), data=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_all_orders_for_event_as_organizer(member, event):
    """
    A member of an organizer group should be able to list all orders for an event.
    """
    add_user_to_group_with_name(member, AdminGroup.SOSIALEN)
    organizer = Group.objects.get(name=AdminGroup.SOSIALEN)

    event.organizer = organizer
    event.save()

    orders = [OrderFactory(event=event) for _ in range(3)]

    url = f"{API_ORDERS_BASE_URL}event/{event.id}/"
    client = get_api_client(user=member)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == len(orders)


@pytest.mark.django_db
def test_list_all_orders_for_event_as_non_organizer(member, event):
    """
    A member of a group that is not the organizer should not be able to list all orders for an event.
    """
    add_user_to_group_with_name(member, AdminGroup.NOK)
    GroupFactory(name=AdminGroup.KOK)
    organizer = Group.objects.get(name=AdminGroup.KOK)

    event.organizer = organizer
    event.save()

    [OrderFactory(event=event) for _ in range(3)]

    url = f"{API_ORDERS_BASE_URL}event/{event.id}/"
    client = get_api_client(user=member)

    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
