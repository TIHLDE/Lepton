from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.wasted.serializers.session import SessionSerializer


class SessionViewset(BaseViewSet):
    serializer_class = SessionSerializer
    permission_classes = [BasicViewPermission]
