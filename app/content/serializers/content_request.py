from rest_framework.relations import SlugRelatedField

from app.common.serializers import BaseModelSerializer
from app.content.models import News
from app.content.models.content_request import ContentRequest
from app.content.serializers import NewsSerializer
from app.content.serializers.user import DefaultUserSerializer
from app.group.models import Group
from app.group.serializers import DefaultGroupSerializer


class ContentRequestSerializer(BaseModelSerializer):
    requester = DefaultUserSerializer(read_only=True)
    recipient_group = DefaultGroupSerializer(read_only=True)
    subject_news = NewsSerializer()

    class Meta:
        model = ContentRequest
        fields = (
            "preferred_publish_date",
            "scheduled_publish_date",
            "status",
            "requester",
            "recipient_group",
            "subject_news",
        )


class ContentRequestCreateSerializer(ContentRequestSerializer):
    recipient_group = SlugRelatedField(queryset=Group.objects.all(), slug_field="slug")

    class Meta:
        model = ContentRequest
        fields = ("preferred_publish_date", "recipient_group", "subject_news")

    def create(self, validated_data):
        # TODO: what can be moved to the model?
        print(validated_data)
        news = validated_data.pop("subject_news", None)
        print(validated_data)
        content_request = super().create(validated_data)

        if news:
            news["is_published"] = True
            print(news)
            news = News(**news)
            news.save()
        print(news)

        content_request.subject_news = news
        requester = self.get_user()
        content_request.requester = requester
        content_request.save()

        return content_request
