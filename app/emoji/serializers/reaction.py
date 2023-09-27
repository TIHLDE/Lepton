from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.emoji.models.reaction import Reaction


class ReactionSerializer(BaseModelSerializer):
    content_type = serializers.CharField(source="content_type.model", read_only=True)
    object_id = serializers.IntegerField()

    class Meta:
        model = Reaction
        fields = ("reaction_id", "user", "emoji", "content_type", "object_id")


#    def create(self, validated_data):
#        content_type_model = validated_data.pop("content_type.model")
#        object_id = validated_data.pop("object_id")
#
#        reaction = Reaction.objects.create(
#            content_type=content_type_model,
#           object_id=object_id,
#            **validated_data
#        )

#        return reaction
