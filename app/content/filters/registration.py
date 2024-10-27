from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from app.common.enums import NativeGroupType as GroupType
from app.content.models.registration import Registration
from app.payment.enums import OrderStatus
from app.payment.models import Order
from django.db.models import Exists, OuterRef


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

    has_paid = filters.BooleanFilter(field_name="event__orders__status", method="filter_has_paid")

    class Meta:
        model = Registration
        fields = ["has_attended", "is_on_wait", "study", "year", "has_allergy", "allow_photo", "has_paid"]

    def filter_study(self, queryset, name, value):
        return queryset.filter(
            user__memberships__group__name__icontains=value,
            user__memberships__group__type=GroupType.STUDY,
        )
    
    def filter_has_paid(self, queryset, name, value):
        sale_order_exists = Order.objects.filter(
            event=OuterRef('event_id'),
            user=OuterRef('user_id'),
            status=OrderStatus.SALE
        )
        
        if value:
            return queryset.filter(Exists(sale_order_exists))
        else:
            return queryset.exclude(Exists(sale_order_exists))


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
