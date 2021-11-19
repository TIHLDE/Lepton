from django_filters.rest_framework import FilterSet

from app.content.models.user import User


class LeaderBoardFilter(FilterSet):
    class Meta:
        model = User
        fields = [
            "user_class",
            "user_study",
            "user_badges__badge__badge_category",
        ]
