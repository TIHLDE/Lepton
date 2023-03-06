from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from emoji import UNICODE_EMOJI_ENGLISH

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.emoji.serializers.custom_emoji import CustomEmojiSerializer

EMOJI_DETAIL = UNICODE_EMOJI_ENGLISH
EMOJI_LIST = list(EMOJI_DETAIL.keys())


class UnicodeEmojiViewSet(BaseViewSet, GenericAPIView):
    permission_classes = [BasicViewPermission]
    serializer_class = CustomEmojiSerializer

    # DRF complains if this is not here, even though it isn't used.
    def get_queryset(self):
        pass

    def list(self, request, *args, **kwargs):
        return Response(EMOJI_LIST)

    # Funker ikke atm
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
