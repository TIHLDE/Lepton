from rest_framework import serializers

from app.blitzed.enums import TournamentStatus
from app.blitzed.exceptions import APIDrawMatch, APIInvalidResult
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


class PongResultCreateSerializer(serializers.ModelSerializer):
    winner = PongTeamSerializer(required=False)

    class Meta:
        model = PongResult
        fields = ("id", "match", "result", "winner")

    def create(self, validated_data):
        result = validated_data.pop("result")
        match = validated_data.pop("match")
        winner = _get_winner(result, match.id)

        next_match = match.future_match
        if next_match is not None:
            if next_match.team1 is None:
                next_match.team1 = winner
            elif next_match.team2 is None:
                next_match.team2 = winner
            next_match.save()
        else:
            tournament = match.tournament
            tournament.status = TournamentStatus.FINISHED
            tournament.save()

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
        winner = _get_winner(result, match.id)
        updated_result = super().update(
            instance, dict(match=match, winner=winner, result=result)
        )

        self.update_match_tree(match, winner)
        return updated_result

    def update_match_tree(self, match, winner):
        if match.future_match is None:
            return

        team1 = match.team1
        team2 = match.team2
        stack = [match.future_match]
        while stack:
            current_match = stack.pop()
            if current_match is None:
                continue
            if not self._team_in_match(current_match, team1, team2):
                continue

            if current_match.team1 in {team1, team2}:
                current_match.team1 = winner
            else:
                current_match.team2 = winner

            if PongResult.objects.filter(match=current_match.id).exists():
                result = PongResult.objects.get(match=current_match.id)
                result.winner = winner
                result.save()

            current_match.save()
            stack.append(current_match.future_match)

    def _team_in_match(self, match, team1, team2):
        return team1 in {match.team1, match.team2} or team2 in {
            match.team1,
            match.team2,
        }


def _get_winner(result, match_id):
    try:
        team1_score, team2_score = map(int, result.split("-"))
        if team1_score > team2_score:
            winner = PongMatch.objects.get(id=match_id).team1
        elif team2_score > team1_score:
            winner = PongMatch.objects.get(id=match_id).team2
        else:
            raise APIDrawMatch()
    except ValueError:
        raise APIInvalidResult()
    return winner
