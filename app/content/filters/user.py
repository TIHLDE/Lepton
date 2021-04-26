from django_filters.rest_framework import BooleanFilter, FilterSet, ChoiceFilter
from app.content.models.user import CLASS, STUDY
from app.common.enums import Groups
from app.content.models import User


class UserFilter(FilterSet):
    """ Filters users """
    user_class = ChoiceFilter(choices=CLASS)
    user_study = ChoiceFilter(choices=STUDY)
    is_TIHLDE_member = BooleanFilter(
        method="filter_is_TIHLDE_member", label="Is TIHLDE member"
    )

    class Meta:
        model: User
        fields = ["user_class", "user_study", "is_TIHLDE_member"]

    def filter_is_TIHLDE_member(self, queryset, name, value):
        if value is True:
            return queryset.filter(membership__group__slug=Groups.TIHLDE)
        elif value is False:
            return queryset.exclude(membership__group__slug=Groups.TIHLDE)
        return queryset

