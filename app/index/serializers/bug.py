from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import SimpleUserSerializer
from app.index.models.bug import Bug


class BugListSerializer(BaseModelSerializer):
    author = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Bug
        fields = (
            "id",
            "title",
            "status",
            "created_at",
            "author",
        )
