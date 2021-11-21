import django_filters
from django_filters.rest_framework import FilterSet

from app.content.models.user import User


class BadgeFilter(FilterSet):
    category = django_filters.UUIDFilter(
        field_name="user_badges__badge__badge_category"
    )

    class Meta:
        model = User
        fields = [
            "user_class",
            "user_study",
            "category",
        ]
