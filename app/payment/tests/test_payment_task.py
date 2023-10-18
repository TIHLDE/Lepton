import pytest

from app.content.factories.registration_factory import RegistrationFactory
from app.content.models import Registration
from app.content.util.event_utils import create_vipps_order
from app.payment.enums import OrderStatus
from app.payment.factories.order_factory import OrderFactory
from app.payment.factories.paid_event_factory import PaidEventFactory
from app.payment.tasks import check_if_has_paid


@pytest.fixture()
def order():
    return OrderFactory()


@pytest.fixture()
def registration():
    return RegistrationFactory()


@pytest.mark.django_db
def test_create_vipps_order(order):
    """
    There should be possible to create a vipps order through the vipps API.
    """

    paid_event = PaidEventFactory(price=100.00)
    event = paid_event.event
    order.event = event
    order.save()

    url = create_vipps_order(
        order_id=order.order_id,
        event=order.event,
        transaction_text="test",
        fallback="test",
    )

    order.refresh_from_db()

    assert url is not None
    assert order.payment_link is not None


@pytest.mark.django_db
def test_delete_registration_if_user_has_not_paid(order, registration):
    """
    A registrations should be deleted if the user has not paid within the time limit.
    """
    paid_event = PaidEventFactory(price=100.00)
    event = paid_event.event
    order.event = event
    order.user = registration.user
    order.save()

    create_vipps_order(
        order_id=order.order_id,
        event=order.event,
        transaction_text="test",
        fallback="test",
    )

    check_if_has_paid(
        event_id=order.event.id, registration_id=registration.registration_id
    )

    try:
        registration.refresh_from_db()
    except Registration.DoesNotExist:
        assert True


@pytest.mark.django_db
def test_delete_registration_if_user_has_reserved_order(order, registration):
    """
    A registrations should not be deleted if the user has paid within the time limit.
    """
    paid_event = PaidEventFactory(price=100.00)
    event = paid_event.event
    order.event = event
    order.user = registration.user
    order.save()

    create_vipps_order(
        order_id=order.order_id,
        event=order.event,
        transaction_text="test",
        fallback="test",
    )

    order.status = OrderStatus.RESERVE
    order.save()

    check_if_has_paid(
        event_id=order.event.id, registration_id=registration.registration_id
    )

    registration.refresh_from_db()

    assert registration is not None


@pytest.mark.django_db
def test_delete_registration_if_user_has_captured_order(order, registration):
    """
    A registrations should not be deleted if the user has paid within the time limit.
    """
    paid_event = PaidEventFactory(price=100.00)
    event = paid_event.event
    order.event = event
    order.user = registration.user
    order.save()

    create_vipps_order(
        order_id=order.order_id,
        event=order.event,
        transaction_text="test",
        fallback="test",
    )

    order.status = OrderStatus.CAPTURE
    order.save()

    check_if_has_paid(
        event_id=order.event.id, registration_id=registration.registration_id
    )

    registration.refresh_from_db()

    assert registration is not None


@pytest.mark.django_db
def test_delete_registration_if_user_has_paid_order(order, registration):
    """
    A registrations should not be deleted if the user has paid within the time limit.
    """
    paid_event = PaidEventFactory(price=100.00)
    event = paid_event.event
    order.event = event
    order.user = registration.user
    order.save()

    create_vipps_order(
        order_id=order.order_id,
        event=order.event,
        transaction_text="test",
        fallback="test",
    )

    order.status = OrderStatus.SALE
    order.save()

    check_if_has_paid(
        event_id=order.event.id, registration_id=registration.registration_id
    )

    registration.refresh_from_db()

    assert registration is not None
