from django.db.models.query_utils import Q
from django_filters.rest_framework import (
    BooleanFilter,
    FilterSet,
    MultipleChoiceFilter,
)

from app.career.enums import JobPostType
from app.career.models.job_post import JobPost
from app.common.filters import NumberInFilter
from app.util.utils import yesterday


class JobPostFilter(FilterSet):
    expired = BooleanFilter(method="filter_expired", label="Expired")
    job_type = MultipleChoiceFilter(choices=JobPostType.choices)
    classes = NumberInFilter(method="filter_classes")

    class Meta:
        model: JobPost
        fields = ["expired", "job_type"]

    def filter_expired(self, queryset, _name, value):
        if value:
            return queryset.filter(deadline__lt=yesterday()).order_by("-deadline")
        return queryset.filter(deadline__gte=yesterday()).order_by("deadline")

    def filter_classes(self, queryset, _name, value):
        query = Q()
        for year in value:
            query |= Q(class_start__lte=year, class_end__gte=year)
        return queryset.filter(query)
