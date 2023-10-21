from rest_framework import serializers

from app.blitzed.models.beerpong_tournament import BeerpongTournament
from app.blitzed.models.pong_team import PongTeam
from app.common.serializers import BaseModelSerializer


class PongTeamSerializer(BaseModelSerializer):
    class Meta:
        model = PongTeam
        fields = ("team_name", "members", "anonymous_members")


class PongTeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PongTeam
        fields = ("team_name", "members", "anonymous_members", "tournamnet_id")

    def create(self, validated_data):
        members = validated_data.pop("members")
        team_name = validated_data.pop("team_name")
        tournament_id = validated_data.pop("tournament_id")
        anonymous_members = validated_data.pop("anonymous_members")

        tournament = BeerpongTournament.objects.get(id=int(tournament_id))
        created_team = tournament.teams.create(
            anonymous_members=anonymous_members,
            team_name=team_name,
            members=members,
        )
        return created_team


class PongTeamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PongTeam
        fields = ("team_name", "members", "anonymous_members", "tournamnet_id")

    def create(self, validated_data):
        members = validated_data.pop("members")
        team_name = validated_data.pop("team_name")
        tournament_id = validated_data.pop("tournament_id")
        anonymous_members = validated_data.pop("anonymous_members")

        tournament = BeerpongTournament.objects.get(id=int(tournament_id))
        created_team = tournament.teams.update(
            anonymous_members=anonymous_members,
            team_name=team_name,
            members=members,
        )
        return created_team
