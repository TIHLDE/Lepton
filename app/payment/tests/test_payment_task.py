from django.utils import timezone

import pytest

from app.content.factories import EventFactory, RegistrationFactory
from app.payment.enums import OrderStatus
from app.payment.factories import OrderFactory
from app.payment.tasks import check_if_has_paid, sweep_expired_unpaid_registrations
from app.payment.util.order_utils import check_if_order_is_paid, is_expired


@pytest.fixture()
def event():
    return EventFactory()


@pytest.fixture()
def registration(event):
    return RegistrationFactory(event=event)


@pytest.mark.django_db
def test_move_registration_to_waitlist_if_no_orders(event, registration):
    """Should move registration to waiting list if user has no orders."""

    check_if_has_paid(event.id, registration.registration_id)

    registration.refresh_from_db()

    assert registration.is_on_wait
    assert registration.payment_expiredate is None


@pytest.mark.django_db
def test_move_registration_to_waitlist_if_no_paid_orders(event, registration):
    """Should move registration to waiting list if user has no paid orders."""

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

    registration.refresh_from_db()

    assert registration.is_on_wait
    assert registration.payment_expiredate is None


@pytest.mark.django_db
def test_skip_registration_already_on_waitlist(event):
    """Should not modify registration that is already on the waiting list."""

    registration = RegistrationFactory(event=event, is_on_wait=True)

    check_if_has_paid(event.id, registration.registration_id)

    registration.refresh_from_db()

    assert registration.is_on_wait


@pytest.mark.django_db
def test_move_to_waitlist_sets_created_at_to_now(event, registration):
    """Should update created_at to now so user goes to bottom of waiting list."""

    original_created_at = registration.created_at

    check_if_has_paid(event.id, registration.registration_id)

    registration.refresh_from_db()

    assert registration.is_on_wait
    assert registration.created_at > original_created_at


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
    assert not registration.is_on_wait


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
    assert not registration.is_on_wait


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
    assert not registration.is_on_wait


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


@pytest.mark.django_db
def test_if_registration_payment_date_is_expired(registration):
    """Should return true if registration payment date is expired."""

    registration.payment_expiredate = timezone.now() - timezone.timedelta(seconds=1)
    registration.save()

    assert is_expired(registration.payment_expiredate)

    registration.payment_expiredate = timezone.now()
    registration.save()

    assert is_expired(registration.payment_expiredate)


@pytest.mark.django_db
def test_if_registration_payment_date_is_not_expired(registration):
    """Should return false if registration payment date is not expired."""

    registration.payment_expiredate = timezone.now() + timezone.timedelta(seconds=1)
    registration.save()

    assert not is_expired(registration.payment_expiredate)


@pytest.mark.django_db
def test_sweep_moves_expired_unpaid_registrations_to_waitlist(event):
    """Sweep task should move expired unpaid registrations to waiting list."""

    registration = RegistrationFactory(event=event, is_on_wait=False)
    registration.payment_expiredate = timezone.now() - timezone.timedelta(hours=1)
    registration.save()

    sweep_expired_unpaid_registrations()

    registration.refresh_from_db()

    assert registration.is_on_wait
    assert registration.payment_expiredate is None


@pytest.mark.django_db
def test_sweep_keeps_paid_registrations(event):
    """Sweep task should not move registrations with paid orders."""

    registration = RegistrationFactory(event=event, is_on_wait=False)
    registration.payment_expiredate = timezone.now() - timezone.timedelta(hours=1)
    registration.save()

    order = OrderFactory(event=event, user=registration.user)
    order.status = OrderStatus.SALE
    order.save()

    sweep_expired_unpaid_registrations()

    registration.refresh_from_db()

    assert not registration.is_on_wait


@pytest.mark.django_db
def test_sweep_ignores_registrations_with_future_expiry(event):
    """Sweep task should not touch registrations whose payment window is still open."""

    registration = RegistrationFactory(event=event, is_on_wait=False)
    registration.payment_expiredate = timezone.now() + timezone.timedelta(hours=1)
    registration.save()

    sweep_expired_unpaid_registrations()

    registration.refresh_from_db()

    assert not registration.is_on_wait
