from rest_framework import viewsets

from app.common.permissions import BasicViewPermission
from app.forms.models.forms import Submission
from app.forms.serializers.submission import SubmissionSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    permission_classes = [BasicViewPermission]
