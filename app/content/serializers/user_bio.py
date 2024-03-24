from app.common.serializers import BaseModelSerializer
from app.content.models.user_bio import UserBio


class UserBioSerializer(BaseModelSerializer):
    class Meta:
        model = UserBio
        fields = ["description", "gitHub_link", "linkedIn_link"]


class UserBioCreateSerializer(BaseModelSerializer):
    class Meta:
        model = UserBio
        fields = ["description", "gitHub_link", "linkedIn_link"]

    def create(self, validated_data):
        return super().create(validated_data)


class UserBioUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = UserBio
        fields = ["description", "gitHub_link", "linkedIn_link"]
