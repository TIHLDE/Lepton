from rest_framework import viewsets

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
