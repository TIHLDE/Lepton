from django_filters.rest_framework import FilterSet, OrderingFilter

from app.payment.models import Order


class OrderFilter(FilterSet):
    """Filters orders"""

    ordering = OrderingFilter(fields=("created_at",))

    class Meta:
        model = Order
        fields = ["event", "status"]
