from django.db.models import Exists, OuterRef
from django_filters import filters
from django_filters.rest_framework.filterset import FilterSet

from app.payment.models import Order, PaidEvent


class OrderFilter(FilterSet):
    """
    Filters payment orders by user, paid events and status.
    """

    user = filters.CharFilter(method="filter_user")
    event = filters.NumberFilter(method="filter_paid_event")

    class Meta:
        model = Order
        fields = ["user", "event", "status"]

    def filter_user(self, queryset, name, value):
        if value and self.request.user:
            return queryset.filter(user__user_id=self.request.user.user_id)
        return queryset

    def filter_paid_event(self, queryset, name, value):
        return queryset.filter(Exists(PaidEvent.objects.filter(event=value)))
