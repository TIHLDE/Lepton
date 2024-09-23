from django_filters.filters import BooleanFilter
from django_filters.rest_framework import FilterSet

from app.common.enums import NativeMembershipType as MembershipType
from app.group.models import Membership


class MembershipFilter(FilterSet):
    """Filters Membership by membership_type"""

    onlyMembers = BooleanFilter(
        method="filter_membership_type", label="Filter only members"
    )

    class Meta:
        model = Membership
        fields = ["onlyMembers"]

    def filter_membership_type(self, queryset, name, value):
        if value:
            return queryset.filter(membership_type=MembershipType.MEMBER)
        return queryset
