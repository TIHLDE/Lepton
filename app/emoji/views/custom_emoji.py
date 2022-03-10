from app.common.viewsets import BaseViewSet
from app.common.permissions import BasicViewPermission
from app.emoji.serializers import CustomEmojiSerializer


class CustomEmojiViewSet(BaseViewSet):
    serializer = CustomEmojiSerializer
    permission_classes = [BasicViewPermission]
