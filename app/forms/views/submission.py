from rest_framework import viewset

from app.common.enums import AdminGroup
from app.forms.models.forms import Submission
from app.forms.permissions import SubmissionPermissions
from app.forms.serializers.submission import SubmissionSerializer


class SubmissionViewSet(viewset.ModelViewSet):
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    permission_classes = [
        SubmissionPermissions([AdminGroup.HS, AdminGroup.NOK, AdminGroup.INDEX])
    ]
