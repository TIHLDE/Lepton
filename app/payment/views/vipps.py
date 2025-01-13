from django.conf import settings
from app.payment.enums import OrderStatus
from app.payment.util.order_utils import check_if_order_is_paid
from app.payment.util.payment_utils import get_payment_order_status
from rest_framework import status
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.payment.models import Order
from app.payment.serializers import VippsOrderSerialzer, CheckPaymentStatusSerializer

from app.content.models import Event


class VippsViewSet(BaseViewSet):
    permission_classes = [BasicViewPermission]
    serializer_class = VippsOrderSerialzer
    queryset = Order.objects.all()

    def create(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
            data = request.data

            MSN = data.get("merchantSerialNumber")
            if int(MSN) != int(settings.VIPPS_MERCHANT_SERIAL_NUMBER):
                return Response(
                    {"detail": "Merchant serial number matcher ikke"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            transaction_info = data.get("transactionInfo")
            if transaction_info:
                new_status = transaction_info["status"]
                order.status = new_status
                order.save()

            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)
            return Response(
                {"detail": "Kunne ikke oppdatere ordre"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, *args, **kwargs):
        has_changed = False

        serializer = CheckPaymentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_id = serializer.validated_data["event_id"]
        user_id = serializer.validated_data["user_id"]

        orders = self.queryset.filter(user_id=user_id, event_id=event_id)
        if not orders.exists():
            return Response(
                {"message": "No orders found for the user in this event."},
                status=status.HTTP_404_NOT_FOUND,
            )

        for order in orders:
            order_status = get_payment_order_status(order.order_id)
            if order_status != order.status:
                has_changed = True
                order.status = order_status
                order.save()

            if has_changed(order):
                return Response({"is_paid": True}, status=status.HTTP_200_OK)

        return Response({"is_paid": False}, status=status.HTTP_200_OK)
