from django_filters.rest_framework import FilterSet
from django_filters import filters
from app.content.models.registration import Registration


class RegistrationFilter(FilterSet):
    event_has_ended = filters.BooleanFilter(method="filter_event_has_ended")

    class Meta:
        model = Registration
        fields = ["has_attended", "is_on_wait"]

    def filter_event_has_ended(self, queryset, name, value):
        return queryset.filter(
            event_has_ended=value
        )