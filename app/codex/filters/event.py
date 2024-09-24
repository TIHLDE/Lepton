from django_filters.rest_framework import (
    DateTimeFilter,
    FilterSet,
    OrderingFilter,
)

from app.codex.models.event import CodexEvent


class CodexEventFilter(FilterSet):
    """Filters events by tag and expired. Works with search query"""

    end_range = DateTimeFilter(field_name="start_date", lookup_expr="lte")
    start_range = DateTimeFilter(field_name="end_date", lookup_expr="gte")

    ordering = OrderingFilter("start_date", "tag")

    class Meta:
        model = CodexEvent
        fields = ["tag", "end_range", "start_range", "organizer"]
