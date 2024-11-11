from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters.rest_framework import OrderingFilter

from app.feedback.models import Feedback
from app.feedback.models.bug import Bug
from app.feedback.models.idea import Idea


class FeedbackFilter(filters.FilterSet):

    feedback_type = filters.CharFilter(
        method="filter_feedback_type", label="List of feedback type"
    )

    status = filters.CharFilter(
        method="filter_status",
        label="List of feedback status",
    )

    ordering = OrderingFilter(
        fields=(
            "created_at",
            "updated_at",
        )
    )

    def filter_feedback_type(self, queryset, _name, feedback_type):

        if feedback_type == "Idea":
            return queryset.filter(Q(instance_of=Idea))

        elif feedback_type == "Bug":
            return queryset.filter(Q(instance_of=Bug))

        else:
            return queryset

    def filter_status(self, queryset, _name, value):
        return queryset.filter(status=value)

    class Meta:
        model = Feedback
        fields = [
            "title",
            "author",
            "status",
            "created_at",
            "updated_at",
        ]
