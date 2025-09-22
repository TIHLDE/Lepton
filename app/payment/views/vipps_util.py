from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.payment.models import Order
from app.payment.serializers import CheckPaymentSerializer
from app.payment.util.payment_utils import get_payment_order_status


@api_view(["POST"])
def check_vipps_payment(self, request, *args, **kwargs):
    has_changed = False

    serializer = CheckPaymentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    event_id = serializer.validated_data["event_id"]
    user_id = serializer.validated_data["user_id"]

    orders = self.queryset.filter(user_id=user_id, event_id=event_id)

    if not orders.exists():
        return Response(
            {"detail": "Ingen ordre funnet for bruker og arrangement."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not Order.has_update_permission(self.request):
        return Response(
            {"detail": "Du har ikke tilgang til å oppdatere denne ordren."},
            status=status.HTTP_403_FORBIDDEN,
        )

    for order in orders:
        order_status = get_payment_order_status(order.order_id)
        if order_status != order.status:
            has_changed = True
            order.status = order_status
            order.save()

    if has_changed(order):
        return Response(
            {"detail": "Ordrestatusen var feil og har blitt endret."},
            status=status.HTTP_200_OK,
        )
    return Response(
        {"detail": "Ordrestatusen er korrekt og har ikke blitt endret."},
        status=status.HTTP_200_OK,
    )
