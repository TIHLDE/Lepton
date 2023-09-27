from app.payment.enums import OrderStatus


def filter_user_event_orders(orders):
    """
    Filter user payment orders for events, so the user only get
    displayed the paid order for an event. All refunds will be displayed.
    """

    STATUS_PRIORITY = [
        OrderStatus.SALE,
        OrderStatus.RESERVE,
        OrderStatus.CAPTURE,
        OrderStatus.INITIATE,
        OrderStatus.CANCEL
    ]

    filtered_orders = {}
    final_orders = []

    for order in orders:
        if (
            not order.event or
            order.event.expired
        ):
            continue

        if order.status == OrderStatus.REFUND:
            final_orders.append(order)
            continue

        if (
            order.event.id not in filtered_orders or
            STATUS_PRIORITY.index(order.status) < STATUS_PRIORITY.index(filtered_orders[order.event.id].status)
        ):
            filtered_orders[order.event.id] = order
    
    filtered_orders = list(filtered_orders.values())
    final_orders += filtered_orders

    return final_orders