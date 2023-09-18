from app.common.serializers import BaseModelSerializer
from app.emoji.models.toddel_emojis import ToddelEmojis


class ToddelEmojisSerializer(BaseModelSerializer):
    class Meta:
        model = ToddelEmojis
        fields = ("toddel", "emojis_allowed")
