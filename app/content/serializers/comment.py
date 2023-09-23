from rest_framework.serializers import ModelSerializer

from app.content.models import Comment
from app.content.serializers.user import DefaultUserSerializer


class CommentSerializer(ModelSerializer):
    user = DefaultUserSerializer(many=False, required=False)

    class Meta:
        model = Comment
        fields = ("comment_id", "body", "created_at", "updated_at", "user")
