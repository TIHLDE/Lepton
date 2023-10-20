import os
from datetime import datetime

from sentry_sdk import capture_exception

from app.content.exceptions import RefundFailedError
from app.payment.enums import OrderStatus
from app.payment.models import Order
from app.payment.tasks import check_if_has_paid
from app.payment.util.payment_utils import (
    get_new_access_token,
    initiate_payment,
    refund_payment,
)


def start_payment_countdown(event, registration):
    """
    Checks if event is a paid event
    and starts the countdown for payment for an user.
    """

    if not event.is_paid_event or registration.is_on_wait:
        return

    try:
        print("Starting payment countdown for user")
        check_if_has_paid.apply_async(
            args=(event.id, registration.registration_id),
            countdown=get_countdown_time(event),
        )
    except Exception as payment_countdown_error:
        capture_exception(payment_countdown_error)


def get_countdown_time(event):
    paytime = event.paid_information.paytime
    return (paytime.hour * 60 + paytime.minute) * 60 + paytime.second


def create_vipps_order(order_id, event, transaction_text, fallback):
    """
    Creates vipps order, and returns the url.
    """

    access_token = os.environ.get("PAYMENT_ACCESS_TOKEN")
    expires_at = os.environ.get("PAYMENT_ACCESS_TOKEN_EXPIRES_AT")

    if not access_token or datetime.now() >= datetime.fromtimestamp(int(expires_at)):
        (expires_at, access_token) = get_new_access_token()
        os.environ.update({"PAYMENT_ACCESS_TOKEN": access_token})
        os.environ.update({"PAYMENT_ACCESS_TOKEN_EXPIRES_AT": str(expires_at)})

    event_price = int(event.paid_information.price * 100)

    response = initiate_payment(
        amount=event_price,
        order_id=str(order_id),
        access_token=access_token,
        transaction_text=transaction_text,
        fallback=fallback,
    )

    return response["url"]


def refund_vipps_order(order_id, event, transaction_text):
    """
    Refunds vipps order.
    """

    access_token = os.environ.get("PAYMENT_ACCESS_TOKEN")
    expires_at = os.environ.get("PAYMENT_ACCESS_TOKEN_EXPIRES_AT")

    if not access_token or datetime.now() >= datetime.fromtimestamp(int(expires_at)):
        (expires_at, access_token) = get_new_access_token()
        os.environ.update({"PAYMENT_ACCESS_TOKEN": access_token})
        os.environ.update({"PAYMENT_ACCESS_TOKEN_EXPIRES_AT": str(expires_at)})

    event_price = int(event.paid_information.price * 100)

    try:
        refund_payment(
            amount=event_price,
            order_id=str(order_id),
            access_token=access_token,
            transaction_text=transaction_text,
        )

        order = Order.objects.get(order_id=order_id)
        order.status = OrderStatus.REFUND
        order.save()

    except Exception as refund_error:
        capture_exception(refund_error)
        raise RefundFailedError("Tilbakebetaling feilet")
