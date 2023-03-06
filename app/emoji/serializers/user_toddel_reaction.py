from app.common.serializers import BaseModelSerializer
from app.emoji.models.user_toddel_reaction import UserToddelReaction


class UserToddelReactionSerializer(BaseModelSerializer):
    class Meta:
        model = UserToddelReaction
        fields = ("user", "toddel", "emoji")
