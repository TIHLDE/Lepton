from rest_framework import viewsets

from app.common.enums import AdminGroup
from app.forms.serializers import FormPolymorphicSerializer
from app.forms.models import Form

from app.forms.permissions import FormPermissions

class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormPolymorphicSerializer
    queryset = Form.objects.all()
    #permission_classes = [FormPermissions([AdminGroup.HS, AdminGroup.NOK, AdminGroup.INDEX])]

    def get_permissions(self):
        if self.action in ["list", "create", "update"]:
            permission_classes = FormPermissions(list(AdminGroup))
        elif self.action == "retrieve":
            pass  # TODO permission_classes = FormPermissions([please insert group that contains all members])

