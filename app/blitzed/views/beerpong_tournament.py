import random

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from app.blitzed.enums import TournamentAccess, TournamentStatus
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

    def get_queryset(self):
        tournament_name = self.request.query_params.get("name", None)
        pin = self.request.query_params.get("pin", None)
        user = self.request.user

        if tournament_name is not None:
            if user is None:
                return self.queryset.filter(
                    access=TournamentAccess.PUBLIC, name=tournament_name
                )
            return self.queryset.filter(
                Q(access=TournamentAccess.PUBLIC) | Q(creator=user),
                name=tournament_name,
            )
        if pin is not None:
            if user is None:
                return self.queryset.filter(
                    Q(access=TournamentAccess.PUBLIC) | Q(access=TournamentAccess.PIN),
                    pin_code=pin,
                )
            return self.queryset.filter(pin_code=pin)

        return self.queryset.filter(access=TournamentAccess.PUBLIC)

    @action(detail=True, methods=["GET"], url_path="generate")
    def generate_tournament_matches_and_return_matches(self, request, *args, **kwargs):
        try:
            tournament = self.get_object()
            matches = self._generate_tournament(tournament)
            if tournament.status == TournamentStatus.FINISHED:
                return Response(
                    {"detail": "Turneringen er allerede ferdig."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            for i, match in enumerate(matches):
                serializer = PongMatchCreateAndUpdateSerializer(
                    match,
                    data=PongMatchCreateAndUpdateSerializer(match).data,
                    partial=True,
                )
                if serializer.is_valid(raise_exception=True):
                    super().perform_update(serializer)

            tournament.status = TournamentStatus.ACTIVE
            tournament.save()
            serializer = BeerpongTournamentSerializer(tournament)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            PongMatch.objects.filter(tournament=tournament).delete()
            return Response(
                {"detail": "Noe gikk galt ved generering av turneringen."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _generate_tournament(self, tournament):
        PongMatch.objects.filter(tournament=tournament).delete()
        matches = self._create_matches(tournament)
        self._create_match_tree(matches=matches, at=len(matches) - 1, n=1, round=1)
        return matches

    def _create_match_tree(self, matches, at, n, round):
        node1 = at - n
        n *= 2

        node2 = node1 - 1
        root = matches[at]
        if node1 < 0:
            return
        match1 = matches[node1]
        match1.future_match = root

        if node2 < 0:
            return
        match2 = matches[node2]
        match2.future_match = root

        self.create_match_tree(matches, node1, n, round + 1)
        self.create_match_tree(matches, node2, n + 1, round + 1)

    def _create_matches(self, tournament):
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
