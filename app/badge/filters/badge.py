from django_filters import filters
from django_filters.rest_framework.filterset import FilterSet

from app.badge.models import BadgeCategory, UserBadge
from app.badge.models.badge import Badge
from app.content.models import User


class UserWithBadgesFilter(FilterSet):
    category = filters.ModelChoiceFilter(
        method="filter_category",
        field_name="category",
        queryset=BadgeCategory.objects.all(),
    )

    def filter_category(self, queryset, name, value):
        return queryset.filter(user_badges__badge__badge_category=value)

    class Meta:
        model = User
        fields = [
            "user_class",
            "user_study",
            "category",
        ]


class UserWithSpecificBadgeFilter(FilterSet):
    user_class = filters.NumberFilter(method="filter_user_class")
    user_study = filters.NumberFilter(method="filter_user_study")

    def filter_user_class(self, queryset, name, value):
        return queryset.filter(user__user_class=value)

    def filter_user_study(self, queryset, name, value):
        return queryset.filter(user__user_study=value)

    class Meta:
        model = UserBadge
        fields = [
            "user_class",
            "user_study",
        ]


class BadgeFilter(FilterSet):
    class Meta:
        model = Badge
        fields = [
            "badge_category",
        ]
