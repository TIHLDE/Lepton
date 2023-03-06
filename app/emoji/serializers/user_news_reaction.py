from app.common.serializers import BaseModelSerializer
from app.emoji.models.user_news_reaction import UserNewsReaction


class UserNewsReactionSerializer(BaseModelSerializer):
    class Meta:
        model = UserNewsReaction
        fields = ("news", "user", "emoji")
