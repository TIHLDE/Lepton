from django.utils import timezone

from sentry_sdk import capture_exception

from app.celery import app
from app.content.models.event import Event
from app.content.models.registration import Registration
from app.payment.models.order import Order
from app.payment.util.order_utils import has_paid_order
from app.util.tasks import BaseTask


@app.task(bind=True, base=BaseTask)
def check_if_has_paid(_self, event_id, registration_id):
    registration = Registration.objects.filter(registration_id=registration_id).first()
    event = Event.objects.filter(id=event_id).first()

    if not registration or not event:
        return

    if registration.is_on_wait:
        return

    user_orders = Order.objects.filter(event=event, user=registration.user)

    if not user_orders or not has_paid_order(user_orders):
        registration.move_to_waiting_list_for_nonpayment()


@app.task(bind=True, base=BaseTask)
def sweep_expired_unpaid_registrations(_self):
    """Safety-net: find all non-wait registrations with expired payment_expiredate
    and no paid order, and move them back to the waiting list."""
    expired_registrations = Registration.objects.filter(
        is_on_wait=False,
        payment_expiredate__isnull=False,
        payment_expiredate__lt=timezone.now(),
        event__end_date__gt=timezone.now(),
    )

    for registration in expired_registrations:
        user_orders = Order.objects.filter(
            event=registration.event, user=registration.user
        )
        if not has_paid_order(user_orders):
            try:
                registration.move_to_waiting_list_for_nonpayment()
            except Exception as e:
                capture_exception(e)
