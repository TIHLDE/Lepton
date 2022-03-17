from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from app.common.permissions import BasicViewPermission

from emoji import UNICODE_EMOJI_ENGLISH

from app.emoji.serializers.custom_emoji import CustomEmojiSerializer


EMOJI_DETAIL = UNICODE_EMOJI_ENGLISH
EMOJI_LIST = list(EMOJI_DETAIL.keys())


class UnicodeEmojiViewSet(ViewSet, GenericAPIView):
    permission_classes = [BasicViewPermission]
    serializer_class = CustomEmojiSerializer

    def list(self, request, *args, **kwargs):
        return Response(EMOJI_LIST)

    def retrieve(self, request, *args, **kwargs):
        print(request.path)
        # return Response()
        return super().retrieve(request, *args, **kwargs)
