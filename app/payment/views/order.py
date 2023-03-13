from app.payment.models import Order
from app.payment.serializers import OrderSerializer


class OrderViewSet:
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related(["user_id"])

    # def create(self, request, *args, **kwargs):
    #     context = {"order_id": request.order_id}

    # def retrieve_by_id(self, request, order_id):
    #     """ "Returns a spesific order by order id"""
    #     try:
    #         group = self.get_object()
    #     except Exception as e:
    #         print(e)

    
