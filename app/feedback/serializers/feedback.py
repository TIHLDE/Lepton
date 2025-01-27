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
            "image",
            "image_alt",
        )
