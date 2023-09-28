from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.emoji.models.reaction import Reaction


class ReactionSerializer(BaseModelSerializer):
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all()
    )
    object_id = serializers.IntegerField()

    class Meta:
        model = Reaction
        fields = ("reaction_id", "user", "emoji", "content_type", "object_id")
