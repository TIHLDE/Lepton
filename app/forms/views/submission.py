from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from app.common.enums import AdminGroup
from app.common.permissions import IsMember
from app.content.models import User
from app.content.views.event import Event
from app.forms.enums import EventFormType
from app.forms.models.forms import EventForm, Form, Submission
from app.forms.permissions import SubmissionPermissions
from app.forms.serializers.submission import SubmissionSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    permission_classes = [
        SubmissionPermissions([AdminGroup.HS, AdminGroup.NOK, AdminGroup.INDEX])
    ]
