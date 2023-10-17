import os
from datetime import datetime

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
        check_if_has_paid.apply_async(
            args=(event.id, registration.registration_id),
            countdown=get_countdown_time(event),
        )
    except Exception as e:
        print(e)


def get_countdown_time(event):
    paytime = event.paid_information.paytime
    return (paytime.hour * 60 + paytime.minute) * 60 + paytime.second


def create_vipps_order(order_id, event, transaction_text):
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

    refund_payment(
        amount=event_price,
        order_id=str(order_id),
        access_token=access_token,
        transaction_text=transaction_text,
    )


# def create_payment_order(event, request, registration):
#     """
#     Checks if event is a paid event
#     and creates a new Vipps payment order.
#     """
#     print("run")
#     if event.is_paid_event:
#         access_token = os.environ.get("PAYMENT_ACCESS_TOKEN")
#         expires_at = os.environ.get("PAYMENT_ACCESS_TOKEN_EXPIRES_AT")
#         if not access_token or datetime.now() >= datetime.fromtimestamp(
#             int(expires_at)
#         ):
#             (expires_at, access_token) = get_new_access_token()
#             os.environ.update({"PAYMENT_ACCESS_TOKEN": access_token})
#             os.environ.update({"PAYMENT_ACCESS_TOKEN_EXPIRES_AT": str(expires_at)})

#         prev_orders = Order.objects.filter(event=event, user=request.user)
#         has_paid_order = False

#         print(prev_orders)
#         for order in prev_orders:
#             if (
#                 order.status == OrderStatus.CAPTURE
#                 or order.status == OrderStatus.RESERVE
#                 or order.status == OrderStatus.SALE
#             ):
#                 has_paid_order = True
#                 break

#         if not has_paid_order:
#             print("has not paid order")
#             paytime = event.paid_information.paytime

#             expire_date = datetime.now() + timedelta(
#                 hours=paytime.hour, minutes=paytime.minute, seconds=paytime.second
#             )

#             # Create Order
#             order_id = uuid.uuid4()
#             amount = int(event.paid_information.price * 100)
#             res = initiate_payment(amount, str(order_id), event.title, access_token)
#             payment_link = res["url"]
#             order = Order.objects.create(
#                 order_id=order_id,
#                 user=request.user,
#                 event=event,
#                 payment_link=payment_link
#             )
#             order.save()
#             check_if_has_paid.apply_async(
#                 args=(order.order_id, registration.registration_id),
#                 countdown=(paytime.hour * 60 + paytime.minute) * 60 + paytime.second,
#             )
