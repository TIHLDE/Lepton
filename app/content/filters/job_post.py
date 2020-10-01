from django_filters.rest_framework import BooleanFilter, FilterSet

from app.util.utils import yesterday

from ..models import JobPost


class JobPostFilter(FilterSet):
    """ Filters job posts by expired """

    expired = BooleanFilter(method="filter_expired", label="Expired")

    class Meta:
        model: JobPost
        fields = ["expired"]

    def filter_expired(self, queryset, name, value):
        if value:
            return queryset.filter(deadline__lt=yesterday()).order_by("-deadline")
        return queryset.filter(deadline__gte=yesterday()).order_by("deadline")
