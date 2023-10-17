from app.payment.enums import OrderStatus


def check_if_order_is_paid(order):
    if order and (
        order.status == OrderStatus.CAPTURE
        or order.status == OrderStatus.RESERVE
        or order.status == OrderStatus.SALE
    ):
        return True

    return False
