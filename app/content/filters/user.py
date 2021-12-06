from django_filters.rest_framework import BooleanFilter, ChoiceFilter, FilterSet, CharFilter

from app.common.enums import Groups
from app.content.models import User
from app.content.models.strike import Strike
from app.content.models.user import CLASS, STUDY


class UserFilter(FilterSet):
    """ Filters users """

    user_class = ChoiceFilter(choices=CLASS)
    user_study = ChoiceFilter(choices=STUDY)
    is_TIHLDE_member = BooleanFilter(
        method="filter_is_TIHLDE_member", label="Is TIHLDE member"
    )
    has_active_strikes = BooleanFilter(
        method="filter_has_active_strikes", label="List of Users with strikes"
    )
    in_group = CharFilter(
        method="filter_is_in_group", label="Only list users in group"
    )

    class Meta:
        model: User
        fields = ["user_class", "user_study", "has_active_strikes", "is_TIHLDE_member", "in_group"]

    def filter_is_in_group(self, queryset, name, value):
        return queryset.filter(memberships__group__slug=value)

    def filter_is_TIHLDE_member(self, queryset, name, value):
        if value is False:
            return queryset.exclude(memberships__group__slug=Groups.TIHLDE)
        return queryset.filter(memberships__group__slug=Groups.TIHLDE)

    def filter_has_active_strikes(self, queryset, name, value):
        if value is False:
            return queryset.exclude(strikes__in=Strike.objects.active()).distinct()
        return queryset.filter(strikes__in=Strike.objects.active()).distinct()
