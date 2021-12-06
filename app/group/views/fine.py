from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.group.filters.fine import FineFilter
from app.group.mixins import APIFineErrorsMixin
from app.group.models.fine import Fine
from app.group.serializers.fine import FineCreateSerializer, FineSerializer


class FineViewSet(viewsets.ModelViewSet, APIFineErrorsMixin):
    serializer_class = FineSerializer
    permission_classes = [BasicViewPermission]
    queryset = Fine.objects.all()
    filterset_class = FineFilter
    pagination_class = BasePagination

    def get_queryset(self):
        return self.queryset.filter(
            group__slug=self.kwargs["slug"], group__fines_activated=True
        )

    def create(self, request, *args, **kwargs):
        context = {
            "group_slug": kwargs["slug"],
            "created_by": request.id,
            "user_ids": request.data["user"],
            "request": request,
        }

        serializer = FineCreateSerializer(
            many=True, partial=True, data=[request.data], context=context
        )

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": ("Boten ble slettet")}, status=status.HTTP_200_OK)
