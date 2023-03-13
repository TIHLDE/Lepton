from app.common.serializers import BaseModelSerializer
from app.emoji.models.news_emojis import NewsEmojis


class NewsEmojisSerializer(BaseModelSerializer):
    class Meta:
        model = NewsEmojis
        fields = ("news", "emoji")
