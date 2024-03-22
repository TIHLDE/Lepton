from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models import News, User
from app.content.serializers.comment import ChildCommentSerializer
from app.content.serializers.user import DefaultUserSerializer
from app.emoji.serializers.reaction import ReactionSerializer


class SimpleNewsSerializer(BaseModelSerializer):
    class Meta:
        model = News
        fields = (
            "id",
            "created_at",
            "updated_at",
            "image",
            "image_alt",
            "title",
            "header",
        )


class NewsSerializer(SimpleNewsSerializer):
    creator = DefaultUserSerializer(read_only=True)
    reactions = ReactionSerializer(required=False, many=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = SimpleNewsSerializer.Meta.model
        fields = SimpleNewsSerializer.Meta.fields + (
            "creator",
            "body",
            "reactions",
            "emojis_allowed",
            "comments_allowed",
            "comments",
        )

    def get_comments(self, obj):
        comments = obj.comments.filter(parent=None)
        return ChildCommentSerializer(comments, many=True).data

    def create(self, validated_data):
        creator = self.context["request"].data.get("creator", None)
        if creator:
            creator = User.objects.get(user_id=creator)
        return News.objects.create(creator=creator or None, **validated_data)

    def update(self, instance, validated_data):
        creator = self.context["request"].data.get("creator", None)
        if creator:
            creator = User.objects.get(user_id=creator)

        instance.creator = creator
        return super().update(instance, validated_data)


class NewsPublicSerializer(SimpleNewsSerializer):
    creator = DefaultUserSerializer(read_only=True)

    class Meta:
        model = SimpleNewsSerializer.Meta.model
        fields = SimpleNewsSerializer.Meta.fields + (
            "creator",
            "body",
        )
