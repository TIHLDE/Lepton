from app.common.serializers import BaseModelSerializer
from app.content.models import UserBadge
from app.content.serializers import BadgeSerializer, DefaultUserSerializer


class UserBadgeSerializer(BaseModelSerializer):
    user = DefaultUserSerializer(read_only=True)
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ["user", "badge"]
