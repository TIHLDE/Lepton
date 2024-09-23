from django.db.models import Exists, OuterRef
from django_filters import filters
from django_filters.rest_framework.filterset import FilterSet

from app.common.enums import NativeGroupType as GroupType
from app.content.models import Strike
from app.group.models.membership import Membership


class StrikeFilter(FilterSet):
    study = filters.NumberFilter(method="filter_study")
    studyyear = filters.NumberFilter(method="filter_studyyear")

    def filter_study(self, queryset, name, value):
        return queryset.filter(
            Exists(
                Membership.objects.filter(
                    user__id=OuterRef("pk"),
                    group__slug=value,
                    group__type=GroupType.STUDY,
                )
            )
        )

    def filter_studyyear(self, queryset, name, value):
        return queryset.filter(
            Exists(
                Membership.objects.filter(
                    user__id=OuterRef("pk"),
                    group__slug=value,
                    group__type=GroupType.STUDYYEAR,
                )
            )
        )

    class Meta:
        model = Strike
        fields = [
            "study",
            "studyyear",
        ]
