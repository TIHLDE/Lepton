from django_filters.rest_framework.filterset import FilterSet

from app.content.models.user import User
from app.content.models.user_badge import UserBadge


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
