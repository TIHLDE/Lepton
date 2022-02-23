from django_filters.rest_framework import (
    BooleanFilter,
    DateTimeFilter,
    FilterSet,
)

from app.content.models import Event
from app.util.utils import midday, now, yesterday


class EventFilter(FilterSet):
    """ Filters events by category and expired. Works with search query """

    expired = BooleanFilter(method="filter_expired", label="Newest")
    end_range = DateTimeFilter(field_name="start_date", lookup_expr="lte")
    start_range = DateTimeFilter(field_name="end_date", lookup_expr="gte")
    open_for_sign_up = BooleanFilter(
        method="filter_open_for_sign_up",
        label="Filter events that are open for sign up",
    )

    class Meta:
        model = Event
        fields = ["category", "expired", "organizer", "end_range", "start_range"]

    def filter_expired(self, queryset, name, value):
        midday_yesterday = midday(yesterday())
        midday_today = midday(now())
        time = midday_today if midday_today < now() else midday_yesterday
        if value:
            return queryset.filter(end_date__lt=time).order_by("-start_date")
        return queryset.filter(end_date__gte=time).order_by("start_date")

    def filter_open_for_sign_up(self, queryset, name, value):
        if value:
            return queryset.filter(
                sign_up=True,
                start_registration_at__lte=now(),
                end_registration_at__gt=now(),
            )
        return queryset
