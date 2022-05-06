from django.db.models import Exists, OuterRef
from django_filters import filters
from django_filters.rest_framework.filterset import FilterSet

from app.badge.models import BadgeCategory, UserBadge
from app.badge.models.badge import Badge
from app.common.enums import GroupType
from app.content.models import User
from app.group.models.membership import Membership


class UserWithBadgesFilter(FilterSet):
    study = filters.CharFilter(
        method="filter_is_in_study", label="Only list users in study"
    )
    studyyear = filters.CharFilter(
        method="filter_is_in_studyyear", label="Only list users in studyyear"
    )

    category = filters.ModelChoiceFilter(
        method="filter_category",
        field_name="category",
        queryset=BadgeCategory.objects.all(),
    )

    def filter_category(self, queryset, name, value):
        return queryset.filter(user_badges__badge__badge_category=value)

    def filter_is_in_study(self, queryset, name, value):
        return queryset.filter(
            memberships__group__slug=value, memberships__group__type=GroupType.STUDY
        )

    def filter_is_in_studyyear(self, queryset, name, value):
        return queryset.filter(
            memberships__group__slug=value, memberships__group__type=GroupType.STUDYYEAR
        )

    class Meta:
        model = User
        fields = [
            "studyyear",
            "study",
            "category",
        ]


class UserWithSpecificBadgeFilter(FilterSet):
    study = filters.NumberFilter(method="filter_study")
    studyyear = filters.NumberFilter(method="filter_studyyear")

    def filter_study(self, queryset, name, value):
        return queryset.filter(
            Exists(
                Membership.objects.filter(
                    user__user_id=OuterRef("pk"),
                    group__slug=value,
                    group__type=GroupType.STUDY,
                )
            )
        )

    def filter_studyyear(self, queryset, name, value):
        return queryset.filter(
            Exists(
                Membership.objects.filter(
                    user__user_id=OuterRef("pk"),
                    group__slug=value,
                    group__type=GroupType.STUDYYEAR,
                )
            )
        )

    class Meta:
        model = UserBadge
        fields = [
            "study",
            "studyyear",
        ]


class BadgeFilter(FilterSet):
    class Meta:
        model = Badge
        fields = [
            "badge_category",
        ]
