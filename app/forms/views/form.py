from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.enums import AdminGroup
from app.forms.models import Form
from app.forms.permissions import FormPermissions
from app.forms.serializers import FormPolymorphicSerializer


class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormPolymorphicSerializer
    queryset = Form.objects.all()
    permission_classes = [
        FormPermissions([AdminGroup.HS, AdminGroup.NOK, AdminGroup.INDEX])
    ]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Skjemaet ble slettet"}, status=status.HTTP_204_NO_CONTENT)
