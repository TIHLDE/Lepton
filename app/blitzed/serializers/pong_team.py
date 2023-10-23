from app.blitzed.models.pong_team import PongTeam
from app.common.serializers import BaseModelSerializer


class PongTeamSerializer(BaseModelSerializer):
    class Meta:
        model = PongTeam
        fields = ("team_name", "members", "anonymous_members")
