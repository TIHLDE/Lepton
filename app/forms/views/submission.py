from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from app.common.enums import AdminGroup
from app.common.permissions import IsMember
from app.content.models import User
from app.forms.enums import EventFormType
from app.forms.serializers.submission import SubmissionSerializer
from app.forms.models.forms import Submission, Form, EventForm
from app.content.views.event import Event
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


    def create(self, request, *args, **kwargs):
        form = get_object_or_404(Form.objects.all(), kwargs.get("form_id"))
        user = get_object_or_404(User.objects.all(), request.user_id)

        if isinstance(form, EventForm):
            event = get_object_or_404(Event.objects.all(), form.event)

            #if form.type == EventFormType.EVALUATION and user attended.

