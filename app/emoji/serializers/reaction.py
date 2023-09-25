from app.common.serializers import BaseModelSerializer
from app.emoji.models.reaction import Reaction


class ReactionSerializer(BaseModelSerializer):
    class Meta:
        model = Reaction
        fields = ("id", "user", "emoji")
