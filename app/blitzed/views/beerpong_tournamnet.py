from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.blitzed.serializers.beerpong_tournamnet import BeerpongTournamentSerializer


class BeerpongTournamentViewset(BaseViewSet):
    serializer_class = BeerpongTournamentSerializer
    permission_classes = [BasicViewPermission]
    