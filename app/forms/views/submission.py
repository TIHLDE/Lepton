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

    def create(self, request, *args, **kwargs):
        form = get_object_or_404(Form.objects.all(), id=kwargs.get("form_id"))

        if isinstance(form, EventForm):
            user = get_object_or_404(
                User.objects.all(), user_id=request.data.get("user")
            )
            event = form.event

            attended = event.get_queue().filter(user=user).exists()

            # Only allow submission if user has attended event.
            if form.type == EventFormType.EVALUATION and not attended:
                return Response(
                    {"detail": "Du har ikke deltatt på dette arrangementet."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        super().create(request, *args, **kwargs)
