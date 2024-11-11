from django_filters.rest_framework import (
    BooleanFilter,
    DateTimeFilter,
    FilterSet,
    OrderingFilter,
)

from app.content.models import News


class NewsFilter(FilterSet):
    """Filters news"""

    ordering = OrderingFilter(fields=("created_at", "updated_at"))

    class Meta:
        model = News
        fields = ["title", "header", "body", "created_at", "updated_at"]
