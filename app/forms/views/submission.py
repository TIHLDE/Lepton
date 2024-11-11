from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.settings import api_settings

from rest_framework_csv.renderers import CSVRenderer

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.forms.csv_writer import SubmissionsCsvWriter
from app.forms.enums import NativeEventFormType as EventFormType
from app.forms.mixins import APIFormErrorsMixin
from app.forms.models.forms import EventForm, Form, Submission
from app.forms.serializers.submission import SubmissionSerializer


class SubmissionViewSet(APIFormErrorsMixin, BaseViewSet):
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (
        CSVRenderer,
    )  # Order matters. Default first.

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {"form_id": self.kwargs.get("form_id"), "user": self.request.user}
        )
        return context

    def get_queryset(self):
        form_id = self.kwargs.get("form_id")
        queryset = (
            super()
            .get_queryset()
            .filter(form__id=form_id)
            .select_related("user")
            .prefetch_related("answers")
        )
        if hasattr(self, "action") and self.action in ["list", "download"]:
            form = get_object_or_404(Form, id=form_id)
            if isinstance(form, EventForm):
                users_in_event = form.event.registrations.filter(
                    is_on_wait=False
                ).values_list("user", flat=True)
                queryset = queryset.filter(user__in=users_in_event)
        return queryset

    def create(self, request, *args, **kwargs):
        form = get_object_or_404(Form, id=kwargs.get("form_id"))
        if isinstance(form, EventForm):
            user = request.user
            event = form.event
            attended = (
                event.get_participants().filter(user=user, has_attended=True).exists()
            )

            if form.type == EventFormType.EVALUATION and not attended:
                return Response(
                    {"detail": "Du har ikke deltatt på dette arrangementet."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="download")
    def download(self, _request, *_args, **_kwargs):
        """To return the response as csv, include header 'Accept: text/csv."""
        return SubmissionsCsvWriter(self.get_queryset()).write_csv()
