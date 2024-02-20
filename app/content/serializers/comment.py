from app.content.enums import ContentType
from rest_framework import serializers
from app.content.models import Comment
from app.content.models import News
from app.content.models import Event
from app.content.serializers.user import DefaultUserSerializer


class ChildCommentSerializer(serializers.ModelSerializer):
    author = DefaultUserSerializer(many=False, required=False)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "body", "created_at", "updated_at", "author", "children")

    def get_children(self, obj):
        children = Comment.objects.filter(parent=obj)
        return ChildCommentSerializer(children, many=True).data
    
class CommentCreateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(max_length=25)
    content_id = serializers.FloatField()

    class Meta:
        model = Comment
        fields = ("body", "parent", "content_type", "content_id")

    def create(self, validated_data):
        body = validated_data.pop("body")
        parent = validated_data.pop("parent")
        content_type = validated_data.pop("content_type")
        content_id = validated_data.pop("content_id")
        author = validated_data.pop("user")

        if content_type.lower() == ContentType.EVENT:
            event = Event.objects.get(id=int(content_id))
            created_comment = event.comments.create(
                body=body, author=author, parent=parent
            )
            return created_comment
        
        if content_type.lower() == ContentType.NEWS:
            news = News.objects.get(id=int(content_id))
            created_comment = news.comments.create(
                body=body, author=author, parent=parent
            )
            return created_comment
        
class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("body",)

