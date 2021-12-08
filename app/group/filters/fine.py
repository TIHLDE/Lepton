from django_filters.rest_framework import FilterSet

from app.group.models import Fine


class FineFilter(FilterSet):
    class Meta:
        model = Fine
        fields = ["payed", "approved"]
