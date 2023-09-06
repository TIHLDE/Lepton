from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import is_admin_user
from app.common.viewsets import BaseViewSet
from app.payment.filters import OrderFilter
from app.payment.models import Order
from app.payment.serializers import OrderListSerializer, OrderSerializer


class OrderViewSet(BaseViewSet, ActionMixin):
    serializer_class = OrderSerializer
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = OrderFilter
    search_fields = ["user", "event"]

    def get_queryset(self):
        if hasattr(self, "action") and self.action == "list":
            return Order.objects.all()

    def list(self, request):
        """
        Returns list of payment orders.
        """
        if is_admin_user(request):
            serializer = OrderListSerializer(
                self.get_queryset(), context={"request": request}, many=True
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": "Du har ikke tilgang til alle betalingsordrene."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def retrieve(self, request, pk):
        """
        Returns detailed information about the order with the specified pk.
        """
        try:
            if not is_admin_user(request):
                return Response(
                    {"detail": "Du har ikke tilgang til denne betalingsordren."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            order = self.get_object()
            serializer = OrderSerializer(
                order, context={"request": request}, many=False
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist as order_not_exist:
            capture_exception(order_not_exist)
            return Response(
                {"detail": "Fant ikke beatlingsordre."},
                status=status.HTTP_404_NOT_FOUND,
            )
