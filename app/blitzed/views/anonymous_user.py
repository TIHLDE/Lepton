from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.blitzed.serializers.anonymous_user import AnonymousUserSerializer


class AnonymousUserViewset(BaseViewSet):
    serializer_class = AnonymousUserSerializer
    permission_classes = [BasicViewPermission]
    