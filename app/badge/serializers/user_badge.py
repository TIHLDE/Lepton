from app.badge.models import UserBadge
from app.badge.serializers import BadgeSerializer
from app.common.serializers import BaseModelSerializer
from app.content.serializers import DefaultUserSerializer


class UserBadgeSerializer(BaseModelSerializer):
    user = DefaultUserSerializer(read_only=True)
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ["user", "badge"]
