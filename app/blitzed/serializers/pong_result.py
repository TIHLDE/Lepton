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


class PongResultCreateAndUpdateSerializer(serializers.ModelSerializer):
    winner = PongTeamSerializer(required=False)

    class Meta:
        model = PongResult
        fields = ("id", "match", "result", "winner")

    def create(self, validated_data):
        result = validated_data.pop("result")
        match = validated_data.pop("match")
        winner = self.get_winner(result, match.id)

        next_match = match.future_match
        if next_match:
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

    def update(self, instance, validated_data):
        result = validated_data.pop("result")
        match = validated_data.pop("match")
        winner = self.get_winner(result, match.id)
        updated_result = super().update(
            instance, dict(match=match, winner=winner, result=result)
        )

        self.update_match_tree(match.id, winner)
        return updated_result

    def update_match_tree(self, match_id, winner):
        current_match = PongMatch.objects.get(id=match_id)
        if not current_match.future_match:
            return
        if PongResult.objects.filter(match=current_match).exists():
            result = PongResult.objects.get(match=current_match)
            if winner != self.get_winner(result.result, current_match.id):
                return

        next_match = current_match.future_match
        if current_match.team1 == next_match.team1:
            next_match.team1 = winner
        elif current_match.team2 == next_match.team1:
            next_match.team1 = winner
        else:
            next_match.team2 = winner
        self.update_match_tree(next_match.id, winner)
        next_match.save()

    def get_winner(self, result, match_id):
        team1_score, team2_score = map(int, result.split("-"))
        if team1_score > team2_score:
            winner = PongMatch.objects.get(id=match_id).team1
        elif team2_score > team1_score:
            winner = PongMatch.objects.get(id=match_id).team2
        else:
            raise APIDrawMatch()
        return winner
