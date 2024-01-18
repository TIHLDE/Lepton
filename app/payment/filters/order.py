from django_filters.rest_framework import FilterSet

from app.payment.models import Order

class OrderFilter(FilterSet):
    """Filters orders by event"""

    class Meta:
        model = Order
        fields = ["event"]