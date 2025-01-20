from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.payment.serializers import CheckPaymentStatusSerializer
from app.payment.util.payment_utils import get_payment_order_status


@api_view(["POST"])
def check_vipps_payment(self, request, *args, **kwargs):
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
