from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response
from rest_framework.decorators import action

from sentry_sdk import capture_exception

from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission, is_admin_user
from app.common.viewsets import BaseViewSet
from app.content.models import Registration, User, Event
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

    def retrieve(self, request, pk):
        try:
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
    
    @action(detail=False, methods=["GET"], url_path="event/(?P<event_id>\d+)")
    def event_orders(self, request, event_id):
        try:
            if is_admin_user(request):
                orders = Order.objects.filter(event=event_id)
                serializer = OrderListSerializer(
                    orders, context={"request": request}, many=True
                )
                return Response(serializer.data, status.HTTP_200_OK)

            event = Event.objects.filter(id=event_id).first()

            if not event:
                return Response(
                    {"detail": "Fant ikke arrangement."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            organizer = event.organizer

            if not organizer:
                return Response(
                    {"detail": "Du har ikke tilgang til disse betalingsordrene."},
                    status=status.HTTP_403_FORBIDDEN
                )

            has_access_through_organizer = request.user.memberships_with_events_access.filter(group=organizer).exists()

            if not has_access_through_organizer:
                return Response(
                    {"detail": "Du har ikke tilgang til disse betalingsordrene."},
                    status=status.HTTP_403_FORBIDDEN
                )

            orders = Order.objects.filter(event=event)

            serializer = OrderListSerializer(
                orders, context={"request": request}, many=True
            )
            return Response(serializer.data, status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "Det skjedde en feil på serveren."},
                status=status.HTTP_404_NOT_FOUND
            )
