from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models.news import News
from app.emoji.models.reaction import Reaction


class ReactionSerializer(BaseModelSerializer):
    class Meta:
        model = Reaction
        fields = ("reaction_id", "user", "emoji")


class ReactionCreateSerializer(serializers.ModelSerializer):
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all()
    )
    object_id = serializers.IntegerField()

    class Meta:
        model = Reaction
        fields = ("reaction_id", "user", "emoji", "content_type", "object_id")

    def create(self, validated_data):
        user = validated_data.pop("user")
        emoji = validated_data.pop("emoji")
        object_id = validated_data.pop("object_id")
        content_type = validated_data.pop("content_type")

        if content_type.model.lower() == "news":
            news = News.objects.get(id=int(object_id))
            created_reaction = news.reactions.create(
                user=user,
                emoji=emoji,
            )
            return created_reaction


class ReactionUpdateSerializer(serializers.ModelSerializer):
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all()
    )
    object_id = serializers.IntegerField()

    class Meta:
        model = Reaction
        fields = ("reaction_id", "emoji", "content_type", "object_id")

    def create(self, validated_data):
        emoji = validated_data.pop("emoji")
        object_id = validated_data.pop("object_id")
        content_type = validated_data.pop("content_type")

        if content_type.model.lower() == "news":
            news = News.objects.get(id=int(object_id))
            created_reaction = news.reactions.create(
                emoji=emoji,
            )
            return created_reaction