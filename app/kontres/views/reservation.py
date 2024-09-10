from rest_framework.decorators import action

from app.common.viewsets import BaseViewSet
from app.common.permissions import BasicViewPermission
from app.kontres.serializer import ReservationSerializer


class ReservationViewSet(BaseViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [BasicViewPermission]

    def get_queryset(self):
        return None

    def create(self, request, *args, **kwargs):
        return None

    def update(self, request, *args, **kwargs):
        return None

    def destroy(self, request, *args, **kwargs):
        return None

    # Get a simple paginated list with filters
    def list(self, request, *args, **kwargs):
        return None

    # Retrieve a detailed paginated list with filters
    def retrieve(self, request, *args, **kwargs):
        return None

    @action(detail=True, methods=["put"], url_path="state")
    def update_state(self, request, *args, **kwargs):
        return None
