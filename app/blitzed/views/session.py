from app.blitzed.serializers.session import SessionSerializer
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class SessionViewset(BaseViewSet):
    serializer_class = SessionSerializer
    permission_classes = [BasicViewPermission]
