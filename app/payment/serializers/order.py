import uuid

from app.common.serializers import BaseModelSerializer
from app.content.models import Event
from app.content.serializers.user import DefaultUserSerializer
from app.content.util.event_utils import create_vipps_order
from app.payment.models.order import Order


class OrderEventSerializer(BaseModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "title", "image", "start_date", "end_date")


class OrderListSerializer(BaseModelSerializer):
    event = OrderEventSerializer(many=False)
    user = DefaultUserSerializer(many=False)

    class Meta:
        model = Order
        fields = ("order_id", "created_at", "status", "user", "event")


class OrderSerializer(BaseModelSerializer):
    event = OrderEventSerializer(many=False)
    user = DefaultUserSerializer(many=False)

    class Meta:
        model = Order
        fields = ("order_id", "status", "payment_link", "created_at", "event", "user")


class VippsOrderSerialzer(BaseModelSerializer):
    class Meta:
        model = Order
        fields = ("order_id",)


class OrderUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Order
        fields = ("status",)


class OrderCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Order
        fields = ("event",)

    def create(self, validated_data):
        user = validated_data.pop("user")
        event = validated_data.pop("event")

        order_id = uuid.uuid4()
        payment_url = create_vipps_order(
            order_id=order_id,
            event=event,
            transaction_text=f"Betaling for {event.title} - {user.first_name} {user.last_name}",
            fallback=f"/arrangementer/{event.id}",
        )

        order = Order.objects.create(
            order_id=order_id,
            payment_link=payment_url,
            event=event,
            user=user,
        )

        return order
