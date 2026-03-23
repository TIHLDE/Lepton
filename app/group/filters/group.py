from django_filters import MultipleChoiceFilter
from django_filters.rest_framework import BooleanFilter, FilterSet

from app.common.enums import NativeGroupType as GroupType
from app.common.enums import NativeInterestGroupType as InterestGroupType
from app.common.permissions import is_admin_user
from app.group.models import Group


class GroupFilter(FilterSet):
    type = MultipleChoiceFilter(method="filter_type", choices=GroupType.choices)
    subtype = MultipleChoiceFilter(
        method="filter_subtype", choices=InterestGroupType.choices
    )
    overview = BooleanFilter(method="filter_overview", label="Oversikt")

    class Meta:
        model: Group
        fields = ["type", "subtype", "overview"]

    def filter_type(self, queryset, _, value):
        return queryset.filter(type__in=value)

    def filter_subtype(self, queryset, _, value):
        return queryset.filter(subtype__in=value)

    def filter_overview(self, queryset, *_):
        if is_admin_user(self.request):
            return queryset
        return queryset.filter(type__in=GroupType.public_groups())
