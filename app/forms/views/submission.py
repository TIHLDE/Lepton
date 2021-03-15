from rest_framework import viewsets

from app.common.enums import AdminGroup
from app.common.permissions import IsMember
from app.forms.serializers.submission import SubmissionSerializer
from app.forms.models.forms import Submission
from app.forms.permissions import FormPermissions


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    permission_classes = FormPermissions([AdminGroup.HS, AdminGroup.NOK, AdminGroup.INDEX])

    def get_permissions(self):
        # Allow members to submit submissions, but not to do anything else.
        if self.request.method == ["POST"]:
            self.permission_classes = [IsMember]
        return super().get_permissions()
