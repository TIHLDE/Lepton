from rest_polymorphic.serializers import PolymorphicSerializer

from app.common.serializers import BaseModelSerializer
from app.feedback.models import Bug, Feedback, Idea
from app.feedback.serializers import BugListSerializer, IdeaListSerializer


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

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["author"] = user

        return super().create(validated_data)


class BugCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Bug
        fields = (
            "title",
            "description",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["author"] = user

        return super().create(validated_data)


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
