from app.common.serializers import BaseModelSerializer
from app.payment.models.paid_event import PaidEvent


class SimplePaidEventSerializer(BaseModelSerializer):
    class Meta:
        model = PaidEvent
        fields = ("price", "paytime")


class PaidEventCreateSerializer(BaseModelSerializer):
    class Meta:
        model = PaidEvent
        fields = ("price", "paytime")
        extra_kwargs = {
            "price": {"required": False},
            "paytime": {"required": False}
        }
