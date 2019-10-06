# Django Filters and Rest Framework imports
from django_filters.rest_framework import DjangoFilterBackend, BooleanFilter, CharFilter, FilterSet
from rest_framework import filters

# Model imports
from .models import Event, JobPost

# Datetime and other import
from datetime import datetime, timedelta, timezone

class EventFilter(FilterSet):
    """
        Filters events by category and expired. Works with search query
    """
    expired = BooleanFilter(method='filter_expired', label='Newest')

    class Meta:
        model = Event 
        fields = ['category', 'expired']

    """
    @param value: boolean for determining if expired or not is found in querystring
    """
    def filter_expired(self, queryset, name, value): 
        if value:
            return queryset.filter(start__lt=datetime.now(tz=timezone.utc)-timedelta(days=1)).order_by('-start')
        return queryset.filter(start__gte=datetime.now(tz=timezone.utc)-timedelta(days=1)).order_by('start')

class JobPostFilter(FilterSet):
    """
        Filters job posts by expired
    """
    expired = BooleanFilter(method='filter_expired', label='Expired')

    class Meta:
        model: JobPost
        fields = ['expired']

    """
    @param value: boolean for determining if expired or not is found in querystring
    """
    def filter_expired(self, queryset, name, value): 
        if value:
            return queryset.filter(deadline__lt=datetime.now(tz=timezone.utc)-timedelta(days=1)).order_by('-deadline')
        return queryset.filter(deadline__gte=datetime.now(tz=timezone.utc)-timedelta(days=1)).order_by('deadline')