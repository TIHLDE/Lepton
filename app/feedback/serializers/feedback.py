from rest_framework import serializers

from rest_polymorphic.serializers import PolymorphicSerializer

from app.common.serializers import BaseModelSerializer
from app.emoji.serializers.reaction import ReactionSerializer
from app.feedback.models import Bug, Feedback, Idea
from app.feedback.serializers import BugDetailSerializer, IdeaDetailSerializer


class FeedbackListPolymorphicSerializer(PolymorphicSerializer, BaseModelSerializer):
    resource_type_field_name = "feedback_type"

    model_serializer_mapping = {
        Bug: BugDetailSerializer,
        Idea: IdeaDetailSerializer,
    }

    reactions = ReactionSerializer(read_only=True, many=True)

    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = (
            "id",
            "title",
            "status",
            "created_at",
            "author",
            "description",
            "emojis_allowed",
            "assignees",
            "image",
            "image_alt",
            "reactions",
            "upvotes",
            "downvotes",
        )

    def get_upvotes(self, obj):
        print("Getting upvotes")
        return obj.reactions.filter(emoji=":thumbs-up:").count()

    def get_downvotes(self, obj):
        return obj.reactions.filter(emoji=":thumbs-down:").count()
