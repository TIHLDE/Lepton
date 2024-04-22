import random
import string

from rest_framework import serializers

from app.blitzed.enums import TournamentAccess, TournamentStatus
from app.blitzed.models.pong_team import PongTeam
from app.blitzed.models.beerpong_tournament import BeerpongTournament
from app.blitzed.serializers.pong_match import PongMatchSerializer
from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import UserSerializer


class BeerpongTournamentSerializer(BaseModelSerializer):
    status = serializers.CharField(required=False, default=TournamentStatus.PENDING)
    access = serializers.CharField(required=False, default=TournamentAccess.PIN)
    matches = PongMatchSerializer(required=False, many=True)
    pin_code = serializers.CharField(required=False)
    creator = UserSerializer(required=False)
    team_count = serializers.IntegerField(required=False)
    player_count = serializers.IntegerField(required=False)

    class Meta:
        model = BeerpongTournament
        fields = ("id", "name", "matches", "status", "pin_code", "creator", "access", "team_count", "player_count")

    def to_representation(self, instance):
        representation = super(BeerpongTournamentSerializer, self).to_representation(instance)
        
        teams = PongTeam.objects.filter(tournament=instance)
        team_count = teams.count()
        player_count = sum([team.members.count() for team in teams]) + sum([team.anonymous_members.count() for team in teams])
        
        representation['team_count'] = team_count
        representation['player_count'] = player_count
        
        return representation

    def create(self, validated_data):
        name = validated_data.pop("name")
        user = self.context["request"].user

        access_str = validated_data.pop("access")
        access = None
        if access_str in TournamentAccess.__members__:
            access = TournamentAccess[access_str]
        else:
            access = TournamentAccess.PIN

        status = TournamentStatus.PENDING
        pin_code = self._generate_pin_code()
        return BeerpongTournament.objects.create(
            name=name,
            creator=user,
            access=access,
            status=status,
            pin_code=pin_code,
        )

    def _generate_pin_code(self):
        return "".join(random.choices(string.digits, k=4))
