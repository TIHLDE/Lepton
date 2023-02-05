<<<<<<< HEAD
from app.payment.serializers import OrderSerializer
from app.payment.models import Order
=======
from app.payment.serializers.order import OrderSerializer
from app.payment.models.order import Order
>>>>>>> 4255020 (added Order model, view and serializer)


class OrderViewSet():
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related([
        "user_id"
    ])

<<<<<<< HEAD
=======
    def create(self, request, *args, **kwargs):
        context = {
            "order_id": request.id
        }

>>>>>>> 4255020 (added Order model, view and serializer)
    def retrieve_by_id(self, request, order_id):
        """"Returns a spesific order by order id"""
        try:
            group = self.get_object()
        except Exception as e:
            print(e)