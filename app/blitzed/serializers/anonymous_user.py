from app.common.serializers import BaseModelSerializer
from app.blitzed.models.anonymous_user import AnonymousUser


class AnonymousUserSerializer(BaseModelSerializer):
    class Meta:
        model = AnonymousUser
        fields = ("name")
        