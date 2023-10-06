from app.common.serializers import BaseModelSerializer
from app.wasted.models.session import Session


class SessionSerializer(BaseModelSerializer):
    class Meta:
        model = Session
