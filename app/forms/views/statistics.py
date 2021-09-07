from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.forms.models import Form
from app.forms.serializers import FormStatisticsSerializer
from app.forms.views import form


class StatisticsViewSet(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin):
    serializer_class = FormStatisticsSerializer
    queryset = Form.objects.all()
    permission_classes = [BasicViewPermission]

    def list(self, request, *args, **kwargs):
        form_id = self.kwargs.get("form_id", None)
        form = get_object_or_404(Form, id=form_id)
        serializer = FormStatisticsSerializer(form)
        return Response(serializer.data, status=status.HTTP_200_OK)
