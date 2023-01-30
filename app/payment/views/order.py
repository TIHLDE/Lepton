from app.payment.serializers import OrderSerializer
from app.payment.models import Order


class OrderViewSet():
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related([
        "user_id"
    ])

    def retrieve_by_id(self, request, order_id):
        """"Returns a spesific order by order id"""
        try:
            group = self.get_object()
        except Exception as e:
            print(e)