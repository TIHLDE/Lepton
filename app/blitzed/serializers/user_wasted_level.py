from app.blitzed.models.user_wasted_level import UserWastedLevel
from app.common.serializers import BaseModelSerializer


class UserWastedLevelSerializer(BaseModelSerializer):
    class Meta:
        model = UserWastedLevel
        fields = (
            "id",
            "user",
            "session",
            "blood_alcohol_level",
            "timestamp",
        )
