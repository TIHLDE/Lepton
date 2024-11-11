from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import SimpleUserSerializer
from app.feedback.models.bug import Bug


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
            "description",
        )
