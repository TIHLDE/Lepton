from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.forms.mixins import APIFormErrorsMixin
from app.forms.models import Form
from app.forms.serializers.forms import (
    FormPolymorphicSerializer,
    FormSerializer,
)
from app.forms.serializers.statistics import FormStatisticsSerializer


class FormViewSet(APIFormErrorsMixin, BaseViewSet):
    serializer_class = FormPolymorphicSerializer
    queryset = Form.objects.all()
    permission_classes = [BasicViewPermission]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            super().perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def get_queryset(self):
        if self.is_template_list_request():
            return self.queryset.filter(template=True)
        return self.queryset

    def get_serializer_class(self):
        if self.is_template_list_request():
            return FormSerializer
        return super().get_serializer_class()

    def is_template_list_request(self):
        return (
            hasattr(self, "action")
            and self.action == "list"
            and "all" not in self.request.query_params
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Skjemaet ble slettet"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="statistics")
    def statistics(self, request, *args, **kwargs):
        form = self.get_object()
        serializer = FormStatisticsSerializer(form)
        return Response(serializer.data, status=status.HTTP_200_OK)
