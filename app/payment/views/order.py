from app.payment.models import Order
from app.payment.serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from app.common.viewsets import BaseViewSet
from app.common.mixins import ActionMixin


class OrderViewSet(BaseViewSet, ActionMixin):
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related("event")
    # queryset = Order.objects.all()
    
    def list(self, request):
        try:
            queryset = Order.objects.all()
            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        except Exception as e:
            raise Exception(e)
        
    def retrieve(self, request, pk):
        try:
            user = request.query_params.get("user_id")
            event = request.query_params.get("event")
            order = Order.objects.filter(user=user, event=event)[0]
            serializer = OrderSerializer(order, context={"request": request}, many=False)
            return Response(serializer.data, status.HTTP_200_OK)
        except Exception as e:
            raise Exception(e)

    # @action(
    #     detail=True,
    #     methods=["get"],
    #     url_path="order"
    # )
    # def retrieve_order_by_event_and_user(self, request, pk):
    #     try:
    #         print("runs this endpoitn")
    #         order = self.get_object()
    #         print(order)
    #         # serializer = OrderSerializer(queryset, many=True)
    #         # return Response(serializer.data, status.HTTP_200_OK)
    #     except Exception as e:
    #         raise Exception(e)
