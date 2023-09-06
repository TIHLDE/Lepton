import pytest

from app.util.test_utils import get_api_client

API_PAYMENTS_BASE_URL = "/payment/"


def get_payment_order(order_id):
    return f"{API_PAYMENTS_BASE_URL}{order_id}/"


@pytest.mark.django_db
def test_list_payment_orders_as_anonymous_user(default_client):
    """An anonymous user should not be able to list all payment orders."""

    response = default_client.get(API_PAYMENTS_BASE_URL)

    assert response.status_code == 403


@pytest.mark.django_db
def test_list_payment_orders_as_admin_user(admin_user):
    """An admin user should be able to list all payment orders."""

    client = get_api_client(admin_user)
    response = client.get(API_PAYMENTS_BASE_URL)

    assert response.status_code == 200


@pytest.mark.django_db
def test_get_order_as_anonymous_user(default_client, payment_order):
    """An anonymous user should not be able to retrieve a spesific order."""

    url = get_payment_order(payment_order.order_id)
    response = default_client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_get_order_as_admin_user(admin_user, payment_order):
    """An admin user should be able to retrieve a spesific order."""

    url = get_payment_order(payment_order.order_id)
    client = get_api_client(admin_user)
    response = client.get(url)

    assert response.status_code == 200
