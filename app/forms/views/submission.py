from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

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
    permission_classes = [FormPermissions([AdminGroup.HS, AdminGroup.NOK, AdminGroup.INDEX])]

    def get_permissions(self):
        # Allow members to submit submissions, but not to do anything else.
        if self.request.method == ["POST"]:
            self.permission_classes = [IsMember]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        form = get_object_or_404(Form.objects.all(), kwargs.get("form_id"))

        if isinstance(form, EventForm):
            user = get_object_or_404(User.objects.all(), request.user_id)
            event = get_object_or_404(Event.objects.all(), form.event)

            attended = event.get_queue().filter(user=user).exists()

            # Only allow submission if user has attended event.
            if form.type == EventFormType.EVALUATION and not attended:
                return Response(
                    {"detail": "Du har ikke deltatt på dette arrangementet."}, status=status.HTTP_400_BAD_REQUEST
                )

        super().create(request, args, kwargs)
