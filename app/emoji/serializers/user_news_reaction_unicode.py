from app.common.serializers import BaseModelSerializer
from app.emoji.models.user_news_reaction_unicode import UserNewsReactionUnicode


class UserNewsReactionUnicodeSerializer(BaseModelSerializer):
    class Meta:
        model = UserNewsReactionUnicode
        fields = ("news", "user", "emoji")
