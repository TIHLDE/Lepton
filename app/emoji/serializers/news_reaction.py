from app.common.serializers import BaseModelSerializer
from app.emoji.models.news_reaction import NewsReaction


class UserNewsReactionSerializer(BaseModelSerializer):
    class Meta:
        model = NewsReaction
        fields = (
            "reaction",
            "news",
        )
