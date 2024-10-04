from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet

from app.common.enums import Groups
from app.common.enums import NativeGroupType as GroupType
from app.content.models import User
from app.content.models.strike import Strike


class UserFilter(FilterSet):
    """Filters users"""

    study = CharFilter(method="filter_is_in_study", label="Only list users in study")
    studyyear = CharFilter(
        method="filter_is_in_studyyear", label="Only list users in studyyear"
    )
    is_TIHLDE_member = BooleanFilter(
        method="filter_is_TIHLDE_member", label="Is TIHLDE member"
    )
    has_active_strikes = BooleanFilter(
        method="filter_has_active_strikes", label="List of Users with strikes"
    )
    in_group = CharFilter(method="filter_is_in_group", label="Only list users in group")

    has_allowed_photo = BooleanFilter(
        method="filter_has_allowed_photo", label="Has allowed photo"
    )

    class Meta:
        model: User
        fields = [
            "study",
            "studyyear",
            "has_active_strikes",
            "is_TIHLDE_member",
            "in_group",
        ]

    def filter_is_in_study(self, queryset, _name, value):
        return queryset.filter(
            memberships__group__slug=value, memberships__group__type=GroupType.STUDY
        )

    def filter_is_in_studyyear(self, queryset, _name, value):
        return queryset.filter(
            memberships__group__slug=value, memberships__group__type=GroupType.STUDYYEAR
        )

    def filter_is_in_group(self, queryset, _name, value):
        return queryset.filter(memberships__group__slug=value)

    def filter_is_TIHLDE_member(self, queryset, _name, value):
        if value is False:
            return queryset.exclude(memberships__group__slug=Groups.TIHLDE)
        return queryset.filter(memberships__group__slug=Groups.TIHLDE)

    def filter_has_active_strikes(self, queryset, _name, value):
        if value is False:
            return queryset.exclude(strikes__in=Strike.objects.active()).distinct()
        return queryset.filter(strikes__in=Strike.objects.active()).distinct()

    def filter_has_allowed_photo(self, queryset, _name, value):
        return queryset.filter(allows_photo_by_default=value)
