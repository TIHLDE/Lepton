from django_filters.rest_framework import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    OrderingFilter,
)

from app.kontres.models import BookableItem


class BookableItemListFilter(FilterSet):
    """Filter for bookable items""" 
    ordering = OrderingFilter(
        fields=(
            "name",
            "allows_alcohol",
        )
    )

    class Meta:
        model = BookableItem
        fields = ["name", "allows_alcohol"]