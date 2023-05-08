from rest_framework import status
from rest_framework.response import Response

from app.common.mixins import ActionMixin
from app.common.viewsets import BaseViewSet
from app.payment.models import Order
from app.payment.serializers import OrderSerializer


class OrderViewSet(BaseViewSet, ActionMixin):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def retrieve(self, request, pk):
        try:
            user = request.query_params.get("user_id")
            event = request.query_params.get("event")
            order = Order.objects.filter(user=user, event=event)[0]
            serializer = OrderSerializer(
                order, context={"request": request}, many=False
            )
            return Response(serializer.data, status.HTTP_200_OK)
        except Exception as e:
            raise Exception(e)
