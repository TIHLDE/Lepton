from django_filters.rest_framework import (
    BooleanFilter,
    DateTimeFilter,
    FilterSet,
)

from app.content.models import Event
from app.util.utils import now


class EventFilter(FilterSet):
    """Filters events by category and expired. Works with search query"""

    end_range = DateTimeFilter(field_name="start_date", lookup_expr="lte")
    start_range = DateTimeFilter(field_name="end_date", lookup_expr="gte")
    open_for_sign_up = BooleanFilter(
        method="filter_open_for_sign_up",
        label="Filter events that are open for sign up",
    )
    user_favorite = BooleanFilter(
        method="filter_user_favorites",
        label="Filter events that are marked as favorite by current user",
    )

    class Meta:
        model = Event
        fields = ["category", "organizer", "end_range", "start_range"]

    def filter_open_for_sign_up(self, queryset, _name, value):
        if value:
            return queryset.filter(
                sign_up=True,
                start_registration_at__lte=now(),
                end_registration_at__gt=now(),
            )
        return queryset

    def filter_user_favorites(self, queryset, _name, value):
        if value and self.request.user:
            return queryset.filter(favorite_users__user_id=self.request.user.user_id)
        return queryset
