# Django Filters and Rest Framework imports
from django_filters.rest_framework import DjangoFilterBackend, BooleanFilter, FilterSet

# Model imports
from .models import Event

# Datetime and other import
from datetime import datetime, timedelta, timezone

CHECK_IF_EXPIRED = lambda : datetime.now()-timedelta(days=1)

class EventFilter(FilterSet):
    """
        Filters events by category and expired. Works with search query
    """
    expired = BooleanFilter(method='filter_expired', label='Expired')

    class Meta:
        model = Event 
        fields = ['category', 'expired']

    """
    @param value: boolean for determining if expired or not is found in querystring
    """
    def filter_expired(self, queryset, name, value): 
        if value:
            return queryset.filter(start__lt=CHECK_IF_EXPIRED()).order_by('-start')
        return queryset.filter(start__gte=CHECK_IF_EXPIRED()).order_by('start')
