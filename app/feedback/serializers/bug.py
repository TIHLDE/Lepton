from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import SimpleUserSerializer
from app.feedback.models.bug import Bug
from app.emoji.serializers.reaction import ReactionSerializer


class BugSerializer(BaseModelSerializer):
    author = SimpleUserSerializer(read_only=True)

    reactions = ReactionSerializer(read_only=True, many=True)

    class Meta:
        model = Bug
        fields = (
            "id",
            "title",
            "status",
            "created_at",
            "author",
            "description",
            "reactions",
            "image",
        )


class BugCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Bug
        fields = (
            "title",
            "description",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["author"] = user

        return super().create(validated_data)


class BugUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Bug
        fields = (
            "title",
            "description",
            "status",
        )

        def update(self, instance, validated_data):
            return super().update(instance, validated_data)


class BugDetailSerializer(BaseModelSerializer):
    author = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Bug
        fields = (
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "author",
            "url",
            "platform",
            "browser",
            "image",
        )
