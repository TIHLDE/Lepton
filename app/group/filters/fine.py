from django_filters.filters import BooleanFilter
from django_filters.rest_framework import FilterSet

from app.group.models import Fine


class FineFilter(FilterSet):
    """ Filters Membership by membership_type """

    approved = BooleanFilter(
        method="filter_approved", label="Filter only approved fines"
    )
    payed = BooleanFilter(method="filter_payed", label="Filter only payed fines")

    class Meta:
        model = Fine
        fields = ["payed", "approved"]

    def filter_approved(self, queryset, name, value):
        if value:
            return queryset.filter(approved=True)
        return queryset

    def filter_payed(self, queryset, name, value):
        if value:
            return queryset.filter(payed=True)
        return queryset
