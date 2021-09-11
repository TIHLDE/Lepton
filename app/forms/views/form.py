from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.forms.models import Form
from app.forms.serializers import FormPolymorphicSerializer
from app.forms.serializers.statistics import (
    FieldStatisticsSerializer,
    FormStatisticsSerializer,
)


class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormPolymorphicSerializer
    queryset = Form.objects.all()
    permission_classes = [BasicViewPermission]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Skjemaet ble slettet"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="statistics")
    def statistics(self, request, *args, **kwargs):
        form = self.get_object()
        serializer = FormStatisticsSerializer(form)
        return Response(serializer.data, status=status.HTTP_200_OK)
