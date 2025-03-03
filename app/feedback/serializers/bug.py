from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import SimpleUserSerializer
from app.emoji.serializers.reaction import ReactionSerializer
from app.feedback.models.bug import Bug

from rest_framework import serializers

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
            "image",
            "image_alt",
            "reactions",
        )


class BugCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Bug
        fields = (
            "title",
            "description",
            "image",
            "image_alt",
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
            "image",
            "image_alt",
        )

        def update(self, instance, validated_data):
            return super().update(instance, validated_data)


class BugDetailSerializer(BaseModelSerializer):
    author = SimpleUserSerializer(read_only=True)

    reactions = ReactionSerializer(read_only=True, many=True)

    upvotes = serializers.IntegerField(read_only=True)
    downvotes = serializers.IntegerField(read_only=True)

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
            "image_alt",
            "reactions",
            "upvotes",
            "downvotes",
        )
