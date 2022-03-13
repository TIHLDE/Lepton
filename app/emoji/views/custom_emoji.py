from app.common.viewsets import BaseViewSet
from app.common.permissions import BasicViewPermission
from app.emoji.serializers import CustomEmojiSerializer
from app.emoji.models import CustomEmoji


class CustomEmojiViewSet(BaseViewSet):
    serializer_class = CustomEmojiSerializer
    permission_classes = [BasicViewPermission]
    queryset = CustomEmoji.objects.all()
