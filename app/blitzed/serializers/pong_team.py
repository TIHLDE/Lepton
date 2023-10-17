from app.common.serializers import BaseModelSerializer
from app.blitzed.models.pong_team import PongTeam


class PongTeamSerializer(BaseModelSerializer):
    class Meta:
        model = PongTeam
        fields = ("team_name", "members", "anonymous_members")
        