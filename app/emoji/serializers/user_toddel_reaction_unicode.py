from app.common.serializers import BaseModelSerializer
from app.emoji.models.user_toddel_reaction_unicode import (
    UserToddelReactionUnicode,
)


class UserToddelReactionUnicodeSerializer(BaseModelSerializer):
    class Meta:
        model = UserToddelReactionUnicode
        fields = ("user", "toddel", "emoji")
