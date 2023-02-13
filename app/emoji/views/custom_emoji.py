from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.emoji.models import CustomEmoji
from app.emoji.serializers import CustomEmojiSerializer


class CustomEmojiViewSet(BaseViewSet):
    serializer_class = CustomEmojiSerializer
    permission_classes = [BasicViewPermission]
    queryset = CustomEmoji.objects.all()

