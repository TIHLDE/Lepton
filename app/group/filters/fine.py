from django_filters.filters import BooleanFilter
from django_filters.rest_framework import FilterSet

from app.group.models import Fine


class FineFilter(FilterSet):

    approved = BooleanFilter(
        method="filter_approved", label="Filter only approved fines"
    )
    payed = BooleanFilter(method="filter_payed", label="Filter only payed fines")

    not_approved = BooleanFilter(
        method="filter__not_approved", label="Filter only approved fines"
    )
    not_payed = BooleanFilter(
        method="filter_not_payed", label="Filter only payed fines"
    )

    class Meta:
        model = Fine
        fields = ["payed", "approved", "not_payed", "not_approved"]

    def filter_approved(self, queryset, name, value):
        if value:
            return queryset.filter(approved=True)
        return queryset

    def filter_payed(self, queryset, name, value):
        if value:
            return queryset.filter(payed=True)
        return queryset

    def filter_not_payed(self, queryset, name, value):
        if value:
            return queryset.filter(payed=False)
        return queryset

    def filter_not_approved(self, queryset, name, value):
        if value:
            return queryset.filter(approved=False)
        return queryset
