from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import (
    BasicViewPermission,
    is_admin_user,
    is_admin_group_user,
    is_index_user,
)
from app.common.viewsets import BaseViewSet
from app.content.models import Registration, User
from app.payment.filters.order import OrderFilter
from app.payment.models import Order
from app.payment.serializers import (
    OrderCreateSerializer,
    OrderListSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
)
from app.payment.util.order_utils import is_expired


class OrderViewSet(BaseViewSet, ActionMixin):
    permission_classes = [BasicViewPermission]
    serializer_class = OrderListSerializer
    pagination_class = BasePagination
    queryset = Order.objects.all()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = OrderFilter
    search_fields = [
        "order_id",
        "event__title",
        "user__first_name",
        "user__last_name",
        "user__user_id",
    ]

    def list(self, request, *args, **kwargs):
        if is_admin_group_user(request):
            return super().list(request, *args, **kwargs)
        return Response(
            {"detail": "Du har ikke tilgang til å se disse ordrene."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def retrieve(self, request, pk):
        try:
            if not is_admin_group_user(request):
                return Response(
                    {"detail": "Du har ikke tilgang til å se denne ordren."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            order = Order.objects.get(order_id=pk)
            serializer = OrderSerializer(
                order, context={"request": request}, many=False
            )
            return Response(serializer.data, status.HTTP_200_OK)
        except Order.DoesNotExist as order_not_exist:
            capture_exception(order_not_exist)
            return Response(
                {"detail": "Fant ikke beatlingsordre."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, pk):
        try:
            if not is_admin_user(request):
                return Response(
                    {"detail": "Du har ikke tilgang til å oppdatere denne ordren."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            order = Order.objects.get(order_id=pk)
            serializer = OrderUpdateSerializer(
                order, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                order = super().perform_update(serializer)
                serializer = OrderSerializer(
                    order, context={"request": request}, many=False
                )
                return Response(serializer.data, status.HTTP_200_OK)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist as order_not_exist:
            capture_exception(order_not_exist)
            return Response(
                {"detail": "Fant ikke beatlingsordre."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            event = request.data.get("event")
            registration = Registration.objects.get(user=user, event=event)

            if is_expired(registration.payment_expiredate):
                return Response(
                    {"detail": "Din betalingstid er utgått"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = OrderCreateSerializer(
                data=request.data,
                context={"request": request},
            )

            if serializer.is_valid():
                order = super().perform_create(serializer, user=user)
                serializer = OrderSerializer(
                    order, context={"request": request}, many=False
                )

                return Response(serializer.data, status.HTTP_201_CREATED)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist as user_not_exist:
            capture_exception(user_not_exist)
            return Response(
                {"detail": "Fant ikke bruker."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def destroy(self, request, *args, **kwargs):
        if is_index_user(request):
            return super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Du har ikke tilgang til å slette denne ordren."},
            status=status.HTTP_403_FORBIDDEN,
        )
