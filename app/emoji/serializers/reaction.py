from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.emoji.models.reaction import Reaction


class ReactionSerializer(BaseModelSerializer):
    content_type = serializers.CharField(source="content_type.model")
    object_id = serializers.IntegerField()

    class Meta:
        model = Reaction
        fields = ("id", "user", "emoji", "content_type", "object_id")
