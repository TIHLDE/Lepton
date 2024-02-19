from app.common.serializers import BaseModelSerializer
from app.content.exceptions import APIUserBioDuplicate
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
        user = validated_data["user"]

        has_bio = UserBio.objects.filter(user=user).first()

        if has_bio:
            raise APIUserBioDuplicate()

        return super().create(validated_data)


class UserBioUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = UserBio
        fields = ["description", "gitHub_link", "linkedIn_link"]
