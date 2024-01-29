from app.common.serializers import BaseModelSerializer
from app.content.models.user_bio import UserBio

class UserBioSerializer(BaseModelSerializer):
    class Meta:
        model = UserBio
        fields = [
            'description',
            'gitHub_link',
            'linkedIn_link'
        ]