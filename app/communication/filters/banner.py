from django_filters import DateTimeFilter
from django_filters.rest_framework import BooleanFilter, FilterSet

from app.communication.models.banner import Banner
from app.util.utils import now


class BannerFilter(FilterSet):
    end_range = DateTimeFilter(field_name="visible_until", lookup_expr="gte")
    start_range = DateTimeFilter(field_name="visible_from", lookup_expr="lte")
    only_active = BooleanFilter(
        method="filter_only_active",
        label="Filter banners that are active.",
    )

    class Meta:
        model = Banner
        fields = ["visible_from", "visible_until"]

    def filter_only_active(self, queryset, name, value):
        if value:
            return queryset.filter(
                visible_from__lte=now(),
                visible_until__gte=now(),
            )
        return queryset
