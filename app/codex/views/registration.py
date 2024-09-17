from rest_framework import filters, status
from rest_framework.response import Response

from app.codex.models.course import Course
from app.codex.models.registration import CourseRegistration
from app.codex.serializers import (
    RegistrationCreateSerializer,
    RegistrationListSerializer,
)
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class RegistrationViewSet(BaseViewSet):
    serializer_class = RegistrationListSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_queryset(self):
        course_id = self.kwargs.get("course_id")
        return CourseRegistration.objects.filter(course__pk=course_id).select_related(
            "user"
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            registration = self.get_object()
            serializer = RegistrationListSerializer(
                registration, context={"request": request}, many=False
            )
            return Response(serializer.data)
        except CourseRegistration.DoesNotExist:
            return Response(
                {"detail": "Fant ikke påmeldingen for kurset"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = RegistrationCreateSerializer(
                data=data, context={"request": request}
            )

            if serializer.is_valid():
                registration = super().perform_create(serializer, user=request.user)
                serializer = RegistrationListSerializer(
                    registration, context={"request": request}, many=False
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                {"detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"detail": "Kunne ikke opprette påmeldingen for kurset"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Påmeldingen for kurset ble slettet"}, status=status.HTTP_200_OK
        )
