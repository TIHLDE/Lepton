from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.group.models.group import Group
from app.group.models.law import Law
from app.group.serializers.law import LawSerializer


class LawViewSet(BaseViewSet):

    serializer_class = LawSerializer
    permission_classes = [BasicViewPermission]
    queryset = Law.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(group__slug=self.kwargs["slug"])

    def create(self, request, *args, **kwargs):
        group = get_object_or_404(Group, slug=kwargs["slug"])
        law = Law.objects.create(group=group)
        serializer = LawSerializer(law, data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            super().perform_create(serializer)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Loven ble slettet"}, status=status.HTTP_200_OK)
