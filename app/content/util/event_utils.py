import os
import uuid
from datetime import datetime, timedelta
from app.payment.enums import OrderStatus
from app.payment.models.order import Order
from app.payment.util.payment_utils import (
    get_new_access_token,
    initiate_payment,
)
from app.payment.tasks import check_if_has_paid


def create_payment_order(event, request, registration): 
    """
        Checks if event is a paid event
        and creates a new Vipps payment order.
    """

    if event.is_paid_event:
        access_token = os.environ.get("PAYMENT_ACCESS_TOKEN")
        expires_at = os.environ.get("PAYMENT_ACCESS_TOKEN_EXPIRES_AT")
        if not access_token or datetime.now() >= datetime.fromtimestamp(
            int(expires_at)
        ):
            (expires_at, access_token) = get_new_access_token()
            os.environ.update({"PAYMENT_ACCESS_TOKEN": access_token})
            os.environ.update({"PAYMENT_ACCESS_TOKEN_EXPIRES_AT": str(expires_at)})

        prev_orders = Order.objects.filter(event=event, user=request.user)
        has_paid_order = False

        for order in prev_orders:
            if (
                order.status == OrderStatus.CAPTURE
                or order.status == OrderStatus.RESERVE
                or order.status == OrderStatus.SALE
            ):
                has_paid_order = True
                break

        if not has_paid_order:

            paytime = event.paid_information.paytime

            expire_date = datetime.now() + timedelta(
                hours=paytime.hour, minutes=paytime.minute, seconds=paytime.second
            )

            # Create Order
            order_id = uuid.uuid4()
            amount = int(event.paid_information.price * 100)
            res = initiate_payment(amount, str(order_id), event.title, access_token)
            payment_link = res["url"]
            order = Order.objects.create(
                order_id=order_id,
                user=request.user,
                event=event,
                payment_link=payment_link,
                expire_date=expire_date,
            )
            order.save()
            check_if_has_paid.apply_async(
                args=(order.order_id, registration.registration_id),
                countdown=(paytime.hour * 60 + paytime.minute) * 60
                + paytime.second,
            )

