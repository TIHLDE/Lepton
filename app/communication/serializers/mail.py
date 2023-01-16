from app.common.serializers import BaseModelSerializer
from app.communication.models import Mail


class MailGDPRSerializer(BaseModelSerializer):
    class Meta:
        model = Mail
        fields = (
            "id",
            "eta",
            "subject",
            "body",
            "sent",
        )
