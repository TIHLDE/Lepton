from rest_polymorphic.serializers import PolymorphicSerializer
from app.common.serializers import BaseModelSerializer
from app.index.models import Feedback, Bug, Idea
from app.index.serializers import BugListSerializer, IdeaListSerializer

class FeedbackListPolymorphicSerializer(PolymorphicSerializer, BaseModelSerializer):
    resource_type_field_name = "feedback_type"

    model_serializer_mapping = {
        Bug: BugListSerializer,
        Idea: IdeaListSerializer,
    }

    class Meta:
        model = Feedback
        fields = (
            "id", 
            "title",
            "status",
            "created_at",
            "author",
        )