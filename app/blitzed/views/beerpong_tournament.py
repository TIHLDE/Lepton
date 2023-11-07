import random

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.blitzed.models.beerpong_tournament import BeerpongTournament
from app.blitzed.models.pong_match import PongMatch
from app.blitzed.models.pong_team import PongTeam
from app.blitzed.serializers.beerpong_tournament import (
    BeerpongTournamentSerializer,
)
from app.blitzed.serializers.pong_match import (
    PongMatchCreateAndUpdateSerializer,
)
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class BeerpongTournamentViewset(BaseViewSet):
    serializer_class = BeerpongTournamentSerializer
    permission_classes = [BasicViewPermission]
    queryset = BeerpongTournament.objects.all()

    @action(detail=False, methods=["GET"])
    def get_tournament_by_name(self, request, *args, **kwargs):
        tournament_name = request.query_params.get("name")
        tournament = BeerpongTournament.objects.get(name=tournament_name)
        serializer = BeerpongTournamentSerializer(tournament)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"], url_path="generate")
    def generate_tournament_matches_and_return_matches(self, request, *args, **kwargs):
        try:
            tournament = self.get_object()
            matches = self.generate_tournament(tournament)
            serialized_matches = [
                PongMatchCreateAndUpdateSerializer(match).data for match in matches
            ]

            match_counter = 0
            for i, match_data in enumerate(serialized_matches):
                match_instance = matches[i]
                serializer = PongMatchCreateAndUpdateSerializer(
                    match_instance, data=match_data, partial=True
                )
                if serializer.is_valid(raise_exception=True):
                    super().perform_update(serializer)
                    match_counter += 1

            if match_counter < len(serialized_matches):
                return Response(
                    {
                        "detail": f"Klarte ikke generere turnering fullstendig. {match_counter} av {len(serialized_matches)} matches generert"
                    },
                    status=status.HTTP_207_MULTI_STATUS,
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": f"Noe gikk galt ved generering av turneringen: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def generate_tournament(self, tournament):
        PongMatch.objects.filter(tournament=tournament).delete()
        matches = self.create_matches(tournament)
        self.create_match_tree(matches, len(matches) - 1, 1)
        return matches

    def create_match_tree(self, matches, at, n):
        if at - n < 0:
            return
        root = matches[at]
        node1 = matches[at - n]
        node1.future_match = root

        if at - n - 1 < 0:
            return
        node2 = matches[at - n - 1]
        node2.future_match = root

        self.create_match_tree(matches, at - n, n + 1)
        self.create_match_tree(matches, at - n - 1, n + 2)

    def create_matches(self, tournament):
        teams = list(PongTeam.objects.filter(tournament=tournament))
        nr_of_matches = len(teams) - 1
        random.shuffle(teams)
        matches = []
        while len(teams) > 0:
            team1 = teams.pop(0)
            if teams:
                team2 = teams.pop(0)
            else:
                team2 = None
            matches.append(
                PongMatch.objects.create(
                    team1=team1,
                    team2=team2,
                    future_match=None,
                    tournament=tournament,
                )
            )
        for i in range(nr_of_matches - len(matches)):
            matches.append(
                PongMatch.objects.create(
                    team1=None,
                    team2=None,
                    future_match=None,
                    tournament=tournament,
                )
            )
        return matches

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Turnering ble slettet"}, status=status.HTTP_200_OK)
