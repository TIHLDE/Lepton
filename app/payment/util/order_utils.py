from django.db.models import (
    BooleanField,
    Case,
    Count,
    Exists,
    OuterRef,
    Q,
    Value,
    When,
)
from django.utils import timezone

from sentry_sdk import capture_exception

from app.payment.enums import OrderStatus
from app.payment.util.payment_utils import get_payment_order_status

PAID_ORDER_STATUSES = (OrderStatus.SALE, OrderStatus.CAPTURE, OrderStatus.RESERVED)


def annotate_suspicious_payment(queryset):
    from app.payment.models import Order

    paid_orders = Order.objects.filter(
        event=OuterRef("event_id"),
        user=OuterRef("user_id"),
        status__in=PAID_ORDER_STATUSES,
    )
    usable_link = Order.objects.filter(
        event=OuterRef("event_id"),
        user=OuterRef("user_id"),
        status=OrderStatus.INITIATE,
    ).exclude(payment_link="")
    double_paid_pairs = (
        Order.objects.filter(status__in=PAID_ORDER_STATUSES)
        .values("event", "user")
        .annotate(c=Count("order_id"))
        .filter(
            c__gte=2,
            event=OuterRef("event_id"),
            user=OuterRef("user_id"),
        )
    )
    missing_payment = Q(_has_paid=False) & Q(_has_link=False)
    suspicious_payment = Q(_double_paid=True) | missing_payment

    return queryset.annotate(
        _double_paid=Exists(double_paid_pairs),
        _has_paid=Exists(paid_orders),
        _has_link=Exists(usable_link),
    ).annotate(
        _has_suspicious_payment=Case(
            When(
                Q(event__paid_information__isnull=False)
                & Q(is_on_wait=False)
                & suspicious_payment,
                then=Value(True),
            ),
            default=Value(False),
            output_field=BooleanField(),
        )
    )


def has_paid_order(orders):
    if not orders:
        return False

    for order in orders:
        if check_if_order_is_paid(order):
            return True

    return False


def is_suspicious_registration(registration):
    """A registration is suspicious when its event is paid, the user is not on
    the waiting list, and one of:
      (A) two or more paid orders exist for (user, event) — double-pay, or
      (B) no paid order exists and no usable INITIATE order with a payment_link
          exists — the Vipps button will never appear.
    """
    event = registration.event
    if not event or not getattr(event, "is_paid_event", False):
        return False
    if registration.is_on_wait:
        return False

    orders = list(event.orders.filter(user=registration.user))
    paid_orders = [o for o in orders if o.status in PAID_ORDER_STATUSES]
    if len(paid_orders) >= 2:
        return True
    if paid_orders:
        return False
    has_usable_link = any(
        o.status == OrderStatus.INITIATE and o.payment_link for o in orders
    )
    return not has_usable_link


def check_if_order_is_paid(order):
    if order and (
        order.status == OrderStatus.CAPTURE
        or order.status == OrderStatus.RESERVED
        or order.status == OrderStatus.SALE
    ):
        return True

    return False


def reconcile_orders_from_vipps(orders):
    """For each non-final order, fetch the authoritative status from Vipps
    and persist it. Returns True if any order is now paid.

    Final states (SALE, CAPTURE, RESERVED, REFUND, CANCEL, VOID) are left
    untouched so a stale Vipps response can never overwrite a settled order.
    Per-order failures are sent to Sentry and the loop continues, so a Vipps
    outage degrades to the local view rather than breaking the caller.
    """
    if not orders:
        return False

    for order in orders:
        if order.status != OrderStatus.INITIATE:
            continue
        try:
            vipps_status = get_payment_order_status(order.order_id)
            if vipps_status and vipps_status != order.status:
                order.status = vipps_status
                order.save()
        except Exception as e:
            capture_exception(e)

    return has_paid_order(orders)


def is_expired(expire_date):
    return expire_date <= timezone.now()
