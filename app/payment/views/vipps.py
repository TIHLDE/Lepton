from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.payment.models import Order
from app.payment.serializers import VippsOrderSerialzer


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
        except:
            return Response(
                {"detail": "Kunne ikke oppdatere ordre"},
                status=status.HTTP_500_BAD_REQUEST,
            )
