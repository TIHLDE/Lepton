from datetime import timedelta

import pytest

from app.payment.factories.order_factory import OrderFactory
from app.util.utils import now


@pytest.fixture()
def order():
    return OrderFactory()


@pytest.mark.django_db
def test_expired_when_order_has_not_expired(order):
    """Should return False if the order has not expired"""
    order.expire_date = now() + timedelta(hours=1)

    assert not order.expired


@pytest.mark.django_db
def test_expired_when_order_has_expired(order):
    """Should return True if the order has expired"""
    order.expire_date = now() - timedelta(hours=1)

    assert order.expired
