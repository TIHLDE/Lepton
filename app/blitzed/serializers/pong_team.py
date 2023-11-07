from rest_framework import serializers

from app.blitzed.models.pong_team import PongTeam
from app.common.serializers import BaseModelSerializer


class PongTeamSerializer(BaseModelSerializer):
    class Meta:
        model = PongTeam
        fields = ("id", "team_name", "members", "anonymous_members")


class PongTeamCreateAndUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PongTeam
        fields = ("id", "team_name", "members", "anonymous_members", "tournament")
