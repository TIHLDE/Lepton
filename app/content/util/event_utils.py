from sentry_sdk import capture_exception

from app.content.exceptions import RefundFailedError
from app.payment.tasks import check_if_has_paid
from app.payment.util.payment_utils import (
    check_access_token,
    initiate_payment,
    refund_payment,
)


def start_payment_countdown(event, registration, from_wait_list=False):
    """
    Checks if event is a paid event
    and starts the countdown for payment for an user.
    """

    if not event.is_paid_event or registration.is_on_wait:
        return

    try:
        check_if_has_paid.apply_async(
            args=(event.id, registration.registration_id),
            countdown=get_countdown_time(event, from_wait_list),
        )
    except Exception as payment_countdown_error:
        capture_exception(payment_countdown_error)


def get_countdown_time(event, from_wait_list=False):
    if from_wait_list:
        # 12 hours and 10 minutes as seconds
        return (12 * 60 * 60) + (10 * 60)

    # paytime as seconds
    paytime = event.paid_information.paytime
    return (paytime.hour * 60 + paytime.minute + 10) * 60 + paytime.second


def create_vipps_order(order_id, event, transaction_text, fallback):
    """
    Creates vipps order, and returns the url.
    """

    access_token = check_access_token()

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

    access_token = check_access_token()

    event_price = int(event.paid_information.price) * 100

    try:
        refund_payment(
            amount=event_price,
            order_id=str(order_id),
            access_token=access_token,
            transaction_text=transaction_text,
        )

    except Exception as refund_error:
        capture_exception(refund_error)
        raise RefundFailedError()
