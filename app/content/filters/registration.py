from django_filters.rest_framework import FilterSet
from django_filters import rest_framework as filters
from app.common.enums import NativeGroupType as GroupType

from app.content.models.registration import Registration


class RegistrationFilter(FilterSet):

    study = filters.CharFilter(
        field_name="user__groups__name", lookup_expr="icontains", method="filter_study"
    )
    year = filters.CharFilter(
        field_name="user__groups__name", lookup_expr="icontains", method="filter_year"
    )

    has_allergy = filters.BooleanFilter(
        field_name="user__allergy",
        method='filter_has_allergy'
    )

    
    class Meta:
        model = Registration
        fields = ["has_attended", "is_on_wait", "study", "year", "has_allergy"]
    
    def filter_study(self, queryset, name, value):
        return queryset.filter(
            user__memberships__group__name__icontains=value,
            user__memberships__group__type=GroupType.STUDY,
        )

    def filter_year(self, queryset, name, value):
        return queryset.filter(user__memberships__group__name__icontains=value, user__memberships__group__type=GroupType.STUDYYEAR)

    def filter_has_allergy(self, queryset, name, value):
        if value:
            return queryset.exclude(user__allergy__isnull=True).exclude(user__allergy__exact='')
        return queryset
