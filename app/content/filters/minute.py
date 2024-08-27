from django_filters.rest_framework import FilterSet, OrderingFilter

from app.content.models import Minute


class MinuteFilter(FilterSet):
    """Filters minutes"""

    ordering = OrderingFilter(
        fields=("created_at", "updated_at", "title", "author", "tag")
    )

    class Meta:
        model = Minute
        fields = ["author", "title", "tag"]
