from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import SimpleUserSerializer
from app.emoji.serializers.reaction import ReactionSerializer
from app.feedback.models.idea import Idea


class IdeaSerializer(BaseModelSerializer):
    author = SimpleUserSerializer(read_only=True)

    reactions = ReactionSerializer(read_only=True, many=True)

    class Meta:
        model = Idea
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


class IdeaCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Idea
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


class IdeaUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Idea
        fields = (
            "title",
            "description",
            "status",
            "image",
            "image_alt",
        )

        def update(self, instance, validated_data):
            return super().update(instance, validated_data)


class IdeaDetailSerializer(BaseModelSerializer):
    author = SimpleUserSerializer(read_only=True)

    reactions = ReactionSerializer(read_only=True, many=True)

    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = (
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "author",
            "image",
            "image_alt",
            "reactions",
            "upvotes",
            "downvotes",
        )

    def get_upvotes(self, obj):
        return obj.reactions.filter(emoji=":thumbs-up:").count()

    def get_downvotes(self, obj):
        return obj.reactions.filter(emoji=":thumbs-down:").count()
