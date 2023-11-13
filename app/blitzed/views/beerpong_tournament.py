import random

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.blitzed.models.beerpong_tournament import BeerpongTournament
from app.blitzed.models.pong_match import PongMatch
from app.blitzed.models.pong_team import PongTeam
from app.blitzed.serializers.beerpong_tournament import (
    BeerpongTournamentGeneratedSerializer,
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

    def get_queryset(self):
        tournament_name = self.request.query_params.get("name", None)
        if tournament_name is not None:
            return BeerpongTournament.objects.filter(name=tournament_name)
        return BeerpongTournament.objects.all()

    @action(detail=True, methods=["GET"], url_path="generate")
    def generate_tournament_matches_and_return_matches(self, request, *args, **kwargs):
        try:
            tournament = self.get_object()
            matches = self.generate_tournament(tournament)

            for i, match in enumerate(matches):
                serializer = PongMatchCreateAndUpdateSerializer(
                    match,
                    data=PongMatchCreateAndUpdateSerializer(match).data,
                    partial=True,
                )
                if serializer.is_valid(raise_exception=True):
                    super().perform_update(serializer)
            serializer = BeerpongTournamentGeneratedSerializer(tournament)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            PongMatch.objects.filter(tournament=tournament).delete()
            return Response(
                {"detail": "Noe gikk galt ved generering av turneringen."},
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
