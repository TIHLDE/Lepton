from rest_framework import viewsets

from app.content.enums import AdminGroup
from app.forms.serializers import FormSerializer
from app.forms.models import Form

from app.forms.permissions import FormPermissions

class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormSerializer
    queryset = Form.objects.all()
    permission_classes = [FormPermissions([AdminGroup.HS, AdminGroup.NOK, AdminGroup.INDEX])]
