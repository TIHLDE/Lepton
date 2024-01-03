from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.mixins import ActionMixin
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import User
from app.payment.models import Order
from app.payment.serializers import OrderCreateSerializer, OrderSerializer
from app.payment.util.order_utils import is_expired


class OrderViewSet(BaseViewSet, ActionMixin):
    permission_classes = [BasicViewPermission]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def retrieve(self, request, pk):
        try:
            user = request.query_params.get("user_id")
            event = request.query_params.get("event")
            orders = Order.objects.filter(user=user, event=event)
            serializer = OrderSerializer(
                orders, context={"request": request}, many=True
            )
            return Response(serializer.data, status.HTTP_200_OK)
        except Order.DoesNotExist as order_not_exist:
            capture_exception(order_not_exist)
            return Response(
                {"detail": "Fant ikke beatlingsordre."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        try:
            user = get_object_or_404(User, user_id=request.id)
            registration = user.registration

            if is_expired(registration.expire_date):
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
