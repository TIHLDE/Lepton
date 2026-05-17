from django.db.models import Count, Exists, OuterRef, Q
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from app.common.enums import NativeGroupType as GroupType
from app.content.models.registration import Registration
from app.payment.enums import OrderStatus
from app.payment.models import Order
from app.payment.util.order_utils import PAID_ORDER_STATUSES


class RegistrationFilter(FilterSet):

    study = filters.CharFilter(
        field_name="user__groups__name", lookup_expr="icontains", method="filter_study"
    )
    year = filters.CharFilter(
        field_name="user__groups__name", lookup_expr="icontains", method="filter_year"
    )

    has_allergy = filters.BooleanFilter(
        field_name="user__allergy", method="filter_has_allergy"
    )

    has_paid = filters.BooleanFilter(
        field_name="event__orders__status", method="filter_has_paid"
    )

    has_suspicious_payment = filters.BooleanFilter(
        method="filter_has_suspicious_payment"
    )

    class Meta:
        model = Registration
        fields = [
            "has_attended",
            "is_on_wait",
            "study",
            "year",
            "has_allergy",
            "allow_photo",
            "has_paid",
            "has_suspicious_payment",
        ]

    def filter_study(self, queryset, name, value):
        return queryset.filter(
            user__memberships__group__name__icontains=value,
            user__memberships__group__type=GroupType.STUDY,
        )

    def filter_has_paid(self, queryset, name, value):
        sale_order_exists = Order.objects.filter(
            event=OuterRef("event_id"),
            user=OuterRef("user_id"),
            status=OrderStatus.SALE,
        )

        if value:
            return queryset.filter(Exists(sale_order_exists))
        else:
            return queryset.exclude(Exists(sale_order_exists))

    def filter_has_suspicious_payment(self, queryset, name, value):
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

        annotated = queryset.filter(
            event__is_paid_event=True, is_on_wait=False
        ).annotate(
            _double_paid=Exists(double_paid_pairs),
            _has_paid=Exists(paid_orders),
            _has_link=Exists(usable_link),
        )
        suspicious = annotated.filter(
            Q(_double_paid=True) | (Q(_has_paid=False) & Q(_has_link=False))
        )

        if value:
            return queryset.filter(pk__in=suspicious.values("pk"))
        return queryset.exclude(pk__in=suspicious.values("pk"))

    def filter_year(self, queryset, name, value):
        return queryset.filter(
            user__memberships__group__name__icontains=value,
            user__memberships__group__type=GroupType.STUDYYEAR,
        )

    def filter_has_allergy(self, queryset, name, value):
        if value:
            return queryset.exclude(user__allergy__isnull=True).exclude(
                user__allergy__exact=""
            )
        return queryset.filter(user__allergy__isnull=True) | queryset.filter(
            user__allergy__exact=""
        )
