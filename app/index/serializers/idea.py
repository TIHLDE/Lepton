from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import SimpleUserSerializer
from app.index.models.idea import Idea


class IdeaListSerializer(BaseModelSerializer):
    author = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Idea
        fields = (
            "id",
            "title",
            "status",
            "created_at",
            "author",
        )
