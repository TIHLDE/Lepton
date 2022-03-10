from app.common.serializers import BaseModelSerializer
from app.emoji.models import CustomEmoji


class CustomEmojiSerializer(BaseModelSerializer):
    class Meta:
        model = CustomEmoji
        fields = ("img", "short_names")
