from app.common.serializers import BaseModelSerializer
from app.content.models.user import User
from app.content.serializers.user import DefaultUserSerializer
from app.payment.models.order import Order


class OrderSerializer:
    pass


class OrderUpdateCreateSerializer(BaseModelSerializer):
    user = DefaultUserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ("order_id", "user", "status", "expire_date")

        read_only_fields = "user"

        def create(self, validated_data):
            user = User.objects.get(user_id=self.context["user_id"])
            return Order.objects.create(user=user, **validated_data)
