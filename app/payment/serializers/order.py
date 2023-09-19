from app.common.serializers import BaseModelSerializer
from app.content.models.event import Event
from app.content.models.user import User
from app.content.serializers.user import DefaultUserSerializer
from app.payment.models.order import Order
from app.util.utils import now


class OrderSerializer(BaseModelSerializer):
    class Meta:
        model = Order
        fields = ("order_id", "status", "expire_date", "payment_link", "event", "user")


class OrderUpdateCreateSerializer(BaseModelSerializer):
    user = DefaultUserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ("order_id", "user", "status", "expire_date")

        read_only_fields = "user"

        def create(self, validated_data):
            user = User.objects.get(user_id=self.context["user_id"])
            paytime = Event.objects.get(
                id=validated_data.get("event")
            ).paid_information.paytime
            return Order.objects.create(
                user=user, expired_date=now() + paytime, **validated_data
            )


class OrderEventListSerializer(BaseModelSerializer):
    class Meta:
        model = Event
        fields = ("title",)


class OrderListSerializer(BaseModelSerializer):
    event = OrderEventListSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ("order_id", "status", "payment_link", "user", "event")
