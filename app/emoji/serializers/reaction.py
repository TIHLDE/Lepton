from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models.news import News
from app.emoji.enums import ContentTypes
from app.emoji.exception import (
    APIContentTypeNotSupportedException,
    APIReactionNotAllowedException,
)
from app.emoji.models.reaction import Reaction


class ReactionSerializer(BaseModelSerializer):
    class Meta:
        model = Reaction
        fields = ("reaction_id", "user", "emoji")


class ReactionCreateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField()

    class Meta:
        model = Reaction
        fields = ("reaction_id", "user", "emoji", "content_type", "object_id")

    def create(self, validated_data):
        user = validated_data.pop("user")
        emoji = validated_data.pop("emoji")
        object_id = validated_data.pop("object_id")
        content_type = validated_data.pop("content_type")
        content_type = ContentType.objects.get(model=content_type)

        object = None
        if content_type.model.lower() == ContentTypes.NEWS:
            object = News.objects.get(id=int(object_id))

        if not object:
            raise APIContentTypeNotSupportedException
        if not object.emojis_allowed:
            raise APIReactionNotAllowedException()

        created_reaction = object.reactions.create(
            user=user,
            emoji=emoji,
        )
        return created_reaction


class ReactionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ("reaction_id", "emoji")

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
