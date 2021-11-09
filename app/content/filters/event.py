from django.db.models import Q
from django_filters.rest_framework import BooleanFilter, FilterSet

from app.content.models import Event
from app.group.models import Group
from app.util.utils import midday, now, yesterday


class EventFilter(FilterSet):
    """ Filters events by category and expired. Works with search query """

    expired = BooleanFilter(method="filter_expired", label="Newest")
    is_admin = BooleanFilter(method="filter_is_admin", label="Is admin")

    class Meta:
        model = Event
        fields = ["category", "expired", "is_admin"]

    def filter_expired(self, queryset, name, value):
        midday_yesterday = midday(yesterday())
        midday_today = midday(now())
        time = midday_today if midday_today < now() else midday_yesterday
        if value:
            return queryset.filter(end_date__lt=time).order_by("-start_date")
        return queryset.filter(end_date__gte=time).order_by("start_date")

    def filter_is_admin(self, queryset, name, value):
        if self.request.user.is_HS_or_Index_member:
            return queryset
        allowed_organizers = Group.objects.filter(
            memberships__in=self.request.user.memberships_with_events_access
        )
        if allowed_organizers.count() == 0:
            return queryset.none()
        return queryset.filter(Q(organizer__in=allowed_organizers) | Q(organizer=None))
