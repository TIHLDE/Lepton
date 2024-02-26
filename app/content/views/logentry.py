from django.contrib.admin.models import LogEntry
from rest_framework.response import Response

from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import AdminGroup, check_has_access
from app.common.viewsets import BaseViewSet
from app.content.serializers.logentry import LogEntryListSerializer


class LogEntryViewSet(BaseViewSet, ActionMixin):
    serializer_class = LogEntryListSerializer
    pagination_class = BasePagination
    queryset = LogEntry.objects.all()

    def list(self, request, *args, **kwargs):
        if check_has_access(AdminGroup.admin(), request):
            return super().list(request, *args, **kwargs)

        return Response({"detail": "Du har ikke tilgang til å se loggen."}, status=403)

    def retrieve(self, request, *args, **kwargs):
        if check_has_access(AdminGroup.admin(), request):
            return super().retrieve(request, *args, **kwargs)

        return Response({"detail": "Du har ikke tilgang til å se loggen."}, status=403)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "Du har ikke tilgang til å logge."}, status=403)

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Du har ikke tilgang til å oppdatere loggen."}, status=403
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Du har ikke tilgang til å slette loggen."}, status=403
        )
