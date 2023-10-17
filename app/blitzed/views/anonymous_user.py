from app.blitzed.serializers.anonymous_user import AnonymousUserSerializer
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class AnonymousUserViewset(BaseViewSet):
    serializer_class = AnonymousUserSerializer
    permission_classes = [BasicViewPermission]
