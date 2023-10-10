from app.common.serializers import BaseModelSerializer
from app.blitzed.models.session import Session


class SessionSerializer(BaseModelSerializer):
    class Meta:
        model = Session
