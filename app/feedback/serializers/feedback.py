from rest_polymorphic.serializers import PolymorphicSerializer

from app.common.serializers import BaseModelSerializer
from app.feedback.models import Bug, Feedback, Idea
from app.feedback.serializers import BugDetailSerializer, IdeaDetailSerializer


class FeedbackListPolymorphicSerializer(PolymorphicSerializer, BaseModelSerializer):
    resource_type_field_name = "feedback_type"

    model_serializer_mapping = {
        Bug: BugDetailSerializer,
        Idea: IdeaDetailSerializer,
    }

    class Meta:
        model = Feedback
        fields = (
            "id",
            "title",
            "status",
            "created_at",
            "author",
            "description",
        )
