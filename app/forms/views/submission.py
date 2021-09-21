from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.forms.enums import EventFormType
from app.forms.models.forms import EventForm, Form, Submission
from app.forms.serializers.submission import SubmissionSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {"form_id": self.kwargs.get("form_id"), "user": self.request.user}
        )
        return context

    def get_queryset(self):
        if hasattr(self, "action") and self.action == "list":
            return self.queryset.filter(form__id=self.kwargs.get("form_id"))
        return self.queryset

    def create(self, request, *args, **kwargs):
        form = get_object_or_404(Form.objects.all(), id=kwargs.get("form_id"))
        if isinstance(form, EventForm):
            user = request.user
            event = form.event
            attended = event.get_queue().filter(user=user, has_attended=True).exists()

            if form.type == EventFormType.EVALUATION and not attended:
                return Response(
                    {"detail": "Du har ikke deltatt på dette arrangementet."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return super().create(request, *args, **kwargs)
