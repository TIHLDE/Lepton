from django_filters import MultipleChoiceFilter
from django_filters.rest_framework import BooleanFilter, FilterSet

from app.common.enums import NativeGroupType as GroupType
from app.common.permissions import is_admin_user
from app.group.models import Group


class GroupFilter(FilterSet):
    type = MultipleChoiceFilter(method="filter_type", choices=GroupType.choices)
    overview = BooleanFilter(method="filter_overview", label="Oversikt")

    class Meta:
        model: Group
        fields = ["type", "overview"]

    def filter_type(self, queryset, _, value):
        """Django Rest does not know hot to convert incoming string values into EnumChoiceField values and we must do this manually."""
        mapped = list(GroupType[v] for v in value)
        return queryset.filter(type__in=mapped)

    def filter_overview(self, queryset, _):
        if is_admin_user(self.request):
            return queryset
        return queryset.filter(type__in=GroupType.public_groups())
