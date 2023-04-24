from app.common.serializers import BaseModelSerializer
from app.content.models import Toddel
from app.emoji.serializers.user_toddel_reaction import (
    UserToddelReactionSerializer,
)


class ToddelSerializer(BaseModelSerializer):
    user_reactions = UserToddelReactionSerializer(
        many=True, required=False, read_only=True
    )

    class Meta:
        model = Toddel
        fields = (
            "created_at",
            "updated_at",
            "image",
            "title",
            "pdf",
            "edition",
            "published_at",
            "user_reactions",
        )
