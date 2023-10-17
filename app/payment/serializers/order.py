import uuid

from app.common.serializers import BaseModelSerializer
from app.content.util.event_utils import create_vipps_order
from app.payment.models.order import Order


class OrderSerializer(BaseModelSerializer):
    class Meta:
        model = Order
        fields = ("order_id", "status", "payment_link")


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
        )

        order = Order.objects.create(
            order_id=order_id,
            payment_link=payment_url,
            event=event,
            user=user,
        )

        return order
