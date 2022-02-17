from django_filters.rest_framework.filterset import FilterSet

from app.badge.models import UserBadge
from app.badge.models.badge import Badge
from app.content.models import User


class UserWithBadgesFilter(FilterSet):
    class Meta:
        model = User
        fields = [
            "user_class",
            "user_study",
            "user_badges__badge__badge_category",
        ]


class UserWithSpecificBadgeFilter(FilterSet):
    class Meta:
        model = UserBadge
        fields = [
            "user__user_class",
            "user__user_study",
        ]


class BadgeFilter(FilterSet):
    class Meta:
        model = Badge
        fields = [
            "badge_category",
        ]
