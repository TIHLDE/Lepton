from app.payment.enums import OrderStatus


def has_paid_order(orders):
    if not orders:
        return False

    for order in orders:
        if check_if_order_is_paid(order):
            return True

    return False


def check_if_order_is_paid(order):
    if order and (
        order.status == OrderStatus.CAPTURE
        or order.status == OrderStatus.RESERVE
        or order.status == OrderStatus.SALE
    ):
        return True

    return False
