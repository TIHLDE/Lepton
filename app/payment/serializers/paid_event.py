from app.common.serializers import BaseModelSerializer
from app.payment.models.paid_event import PaidEvent


class SimplePaidEventSerializer(BaseModelSerializer):

    class Meta:
        model = PaidEvent
        fields = '__all__'


class PaidEventCreateSerializer(BaseModelSerializer):

    class Meta:
        model = PaidEvent
        fields = (
            'price',
        )
