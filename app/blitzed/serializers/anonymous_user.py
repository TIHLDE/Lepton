from app.blitzed.models.anonymous_user import AnonymousUser
from app.common.serializers import BaseModelSerializer


class AnonymousUserSerializer(BaseModelSerializer):
    class Meta:
        model = AnonymousUser
        fields = ["name"]
