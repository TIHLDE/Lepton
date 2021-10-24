from datetime import datetime

from django.db.models import Q
from django_filters.rest_framework import BooleanFilter, FilterSet

from app.common.enums import GroupType, MembershipType
from app.content.models import Event
from app.group.models import Group, Membership
from app.util.utils import midday, yesterday


class EventFilter(FilterSet):
    """ Filters events by category and expired. Works with search query """

    expired = BooleanFilter(method="filter_expired", label="Newest")
    is_admin = BooleanFilter(method="filter_is_admin", label="Is admin")

    class Meta:
        model = Event
        fields = ["category", "expired", "is_admin"]

    def filter_expired(self, queryset, name, value):
        midday_yesterday = midday(yesterday())
        midday_today = midday(datetime.now())
        time = midday_today if midday_today < datetime.now() else midday_yesterday
        if value:
            return queryset.filter(end_date__lt=time).order_by("-start_date")
        return queryset.filter(end_date__gte=time).order_by("start_date")

    def filter_is_admin(self, queryset, name, value):
        if self.request.user.is_HS_or_Index_member:
            return queryset
        allowed_memberships = self.request.user.memberships.filter(
            (
                Q(membership_type=MembershipType.LEADER)
                & (
                    Q(group__type=GroupType.COMMITTEE)
                    | Q(group__type=GroupType.INTERESTGROUP)
                )
            )
            | Q(group__type=GroupType.SUBGROUP)
            | Q(group__type=GroupType.BOARD)
        )
        allowed_groups = Group.objects.filter(memberships__in=allowed_memberships)
        return queryset.filter(Q(group__in=allowed_groups) | Q(group=None))
