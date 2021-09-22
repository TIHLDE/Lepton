from datetime import datetime

from django_filters.rest_framework import BooleanFilter, FilterSet

from app.content.models import Event
from app.util.utils import midday, yesterday


class EventFilter(FilterSet):
    """ Filters events by category and expired. Works with search query """

    expired = BooleanFilter(method="filter_expired", label="Newest")

    class Meta:
        model = Event
        fields = ["category", "expired"]

    def filter_expired(self, queryset, name, value):
        midday_yesterday = midday(yesterday())
        midday_today = midday(datetime.now())
        time = midday_today if midday_today < datetime.now() else midday_yesterday
        if value:
            return queryset.filter(end_date__lt=time).order_by("-end_date")
        return queryset.filter(end_date__gte=time).order_by("end_date")
