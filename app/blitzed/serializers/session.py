from app.blitzed.models.session import Session
from app.common.serializers import BaseModelSerializer


class SessionSerializer(BaseModelSerializer):
    class Meta:
        model = Session
