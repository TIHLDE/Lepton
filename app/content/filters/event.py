from django_filters.rest_framework import BooleanFilter, FilterSet

from ..models import Event
from app.util.utils import yesterday


class EventFilter(FilterSet):
    """ Filters events by category and expired. Works with search query """
    expired = BooleanFilter(method='filter_expired', label='Newest')

    class Meta:
        model = Event
        fields = ['category', 'expired']

    def filter_expired(self, queryset, name, value):
        if value:
            return queryset.filter(start_date__lt=yesterday()).order_by('-start_date')
        return queryset.filter(start_date__gte=yesterday()).order_by('start_date')
