from rest_framework import serializers

from app.blitzed.exceptions import APIDrawMatch
from app.blitzed.models.pong_match import PongMatch
from app.blitzed.models.pong_result import PongResult
from app.blitzed.serializers.pong_team import (
    PongTeamSerializer,
    SimplePongTeamSerializer,
)
from app.common.serializers import BaseModelSerializer


class PongResultSerializer(BaseModelSerializer):
    winner = SimplePongTeamSerializer()

    class Meta:
        model = PongResult
        fields = ("id", "match", "winner", "result")


class PongMatchCreateSerializer(serializers.ModelSerializer):
    winner = PongTeamSerializer(required=False)

    class Meta:
        model = PongResult
        fields = ("id", "match", "result", "winner")

    def create(self, validated_data):
        result = validated_data.pop("result")
        match = validated_data.pop("match")
        winner = get_winner(result, match.id)

        next_match = match.future_match
        if next_match is not None:
            if next_match.team1 is None:
                next_match.team1 = winner
            elif next_match.team2 is None:
                next_match.team2 = winner
            next_match.save()

        return PongResult.objects.create(
            match=match,
            winner=winner,
            result=result,
        )


class PongResultUpdateSerializer(serializers.ModelSerializer):
    winner = PongTeamSerializer(required=False)

    class Meta:
        model = PongResult
        fields = ("id", "result", "winner")

    def update(self, instance, validated_data):
        match = instance.match
        result = validated_data.pop("result")
        winner = get_winner(result, match.id)
        updated_result = super().update(
            instance, dict(match=match, winner=winner, result=result)
        )

        self.update_match_tree(match, winner, match.team1, match.team2)
        return updated_result

    def update_match_tree(self, current_match, winner, team1, team2):
        if current_match.future_match is None:
            return

        next_match = current_match.future_match
        if not self.team_in_match(next_match, team1, team2):
            return

        if next_match.team1 in {team1, team2}:
            next_match.team1 = winner
        else:
            next_match.team2 = winner

        if PongResult.objects.filter(match=next_match.id).exists():
            result = PongResult.objects.get(match=next_match.id)
            result.winner = winner
            result.save()

        next_match.save()
        self.update_match_tree(next_match, winner, team1, team2)

    def team_in_match(self, match, team1, team2):
        return team1 in {match.team1, match.team2} or team2 in {
            match.team1,
            match.team2,
        }


def get_winner(result, match_id):
    team1_score, team2_score = map(int, result.split("-"))
    if team1_score > team2_score:
        winner = PongMatch.objects.get(id=match_id).team1
    elif team2_score > team1_score:
        winner = PongMatch.objects.get(id=match_id).team2
    else:
        raise APIDrawMatch()
    return winner
