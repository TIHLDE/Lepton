from django_filters.rest_framework import FilterSet

from app.content.models.registration import Registration


class RegistrationFilter(FilterSet):

    class Meta:
        model = Registration
        fields = ["has_attended", "is_on_wait"]