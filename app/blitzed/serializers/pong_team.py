from rest_framework import serializers

from app.blitzed.models.pong_team import PongTeam
from app.blitzed.serializers.anonymous_user import AnonymousUserSerializer
from app.common.serializers import BaseModelSerializer


class PongTeamSerializer(BaseModelSerializer):
    anonymous_members = AnonymousUserSerializer(required=False, many=True)

    class Meta:
        model = PongTeam
        fields = ("id", "team_name", "members", "anonymous_members")


class SimplePongTeamSerializer(BaseModelSerializer):
    class Meta:
        model = PongTeam
        fields = ("id", "team_name")


class PongTeamCreateAndUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PongTeam
        fields = ("id", "team_name", "members", "anonymous_members", "tournament")
