import pytest

from app.content.factories import EventFactory, RegistrationFactory
from app.content.models import Registration
from app.payment.enums import OrderStatus
from app.payment.factories import OrderFactory
from app.payment.tasks import check_if_has_paid
from app.payment.util.order_utils import check_if_order_is_paid


@pytest.fixture()
def event():
    return EventFactory()


@pytest.fixture()
def registration(event):
    return RegistrationFactory(event=event)


@pytest.mark.django_db
def test_delete_registration_if_no_orders(event, registration):
    """Should delete registration if user has no orders."""

    check_if_has_paid(event.id, registration.registration_id)

    registration = Registration.objects.filter(
        registration_id=registration.registration_id
    ).first()

    assert not registration


@pytest.mark.django_db
def test_delete_registration_if_no_paid_orders(event, registration):
    """Should delete registration if user has no paid orders."""

    first_order = OrderFactory(event=event, user=registration.user)
    second_order = OrderFactory(event=event, user=registration.user)
    third_order = OrderFactory(event=event, user=registration.user)
    fourth_order = OrderFactory(event=event, user=registration.user)

    first_order.status = OrderStatus.VOID
    first_order.save()
    second_order.status = OrderStatus.INITIATE
    second_order.save()
    third_order.status = OrderStatus.CANCEL
    third_order.save()
    fourth_order.status = OrderStatus.REFUND
    fourth_order.save()

    check_if_has_paid(event.id, registration.registration_id)

    registration = Registration.objects.filter(
        registration_id=registration.registration_id
    ).first()

    assert not registration


@pytest.mark.django_db
def test_keep_registration_if_has_paid_order(event, registration):
    """Should not delete registration if user has paid order."""

    first_order = OrderFactory(event=event, user=registration.user)
    second_order = OrderFactory(event=event, user=registration.user)
    third_order = OrderFactory(event=event, user=registration.user)

    first_order.status = OrderStatus.SALE
    first_order.save()
    second_order.status = OrderStatus.CANCEL
    second_order.save()
    third_order.status = OrderStatus.CANCEL
    third_order.save()

    check_if_has_paid(event.id, registration.registration_id)

    registration.refresh_from_db()

    assert registration


@pytest.mark.django_db
def test_keep_registration_if_has_reserved_order(event, registration):
    """Should not delete registration if user has reserved order."""

    first_order = OrderFactory(event=event, user=registration.user)
    second_order = OrderFactory(event=event, user=registration.user)
    third_order = OrderFactory(event=event, user=registration.user)

    first_order.status = OrderStatus.RESERVED
    first_order.save()
    second_order.status = OrderStatus.CANCEL
    second_order.save()
    third_order.status = OrderStatus.CANCEL
    third_order.save()

    check_if_has_paid(event.id, registration.registration_id)

    registration.refresh_from_db()

    assert registration


@pytest.mark.django_db
def test_keep_registration_if_has_captured_order(event, registration):
    """Should not delete registration if user has captured order."""

    first_order = OrderFactory(event=event, user=registration.user)
    second_order = OrderFactory(event=event, user=registration.user)
    third_order = OrderFactory(event=event, user=registration.user)

    first_order.status = OrderStatus.CAPTURE
    first_order.save()
    second_order.status = OrderStatus.CANCEL
    second_order.save()
    third_order.status = OrderStatus.CANCEL
    third_order.save()

    check_if_has_paid(event.id, registration.registration_id)

    registration.refresh_from_db()

    assert registration


@pytest.mark.django_db
@pytest.mark.parametrize(
    "order_status", [OrderStatus.CAPTURE, OrderStatus.SALE, OrderStatus.RESERVED]
)
def test_if_order_is_paid(order_status):
    """Should return true if order is paid."""

    order = OrderFactory()

    order.status = order_status
    order.save()

    assert check_if_order_is_paid(order)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "order_status",
    [OrderStatus.INITIATE, OrderStatus.VOID, OrderStatus.CANCEL, OrderStatus.REFUND],
)
def test_if_order_is_not_paid(order_status):
    """Should return false if order is not paid."""

    order = OrderFactory()

    order.status = order_status
    order.save()

    assert not check_if_order_is_paid(order)
