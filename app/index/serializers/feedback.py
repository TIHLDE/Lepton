from rest_polymorphic.serializers import PolymorphicSerializer

from app.common.serializers import BaseModelSerializer
from app.index.models import Bug, Feedback, Idea
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

class IdeaCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Idea
        fields = (
            "title",
            "description",
        )


class BugCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Bug
        fields = (
            "title",
            "description",
        )
        
class IdeaUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Feedback
        fields = (
            "title",
            "description",
            "status",
        )

        def update(self, instance, validated_data):
            return super().update(instance, validated_data)
        
class BugUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Feedback
        fields = (
            "title",
            "description",
            "status",
        )

        def update(self, instance, validated_data):
            
            return super().update(instance, validated_data)
        
 
        

