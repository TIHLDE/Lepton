from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response

from app.codex.filters import CourseFilter
from app.codex.models.course import Course
from app.codex.mixins import APICodexCourseErrorsMixin
from app.codex.serializers import (
    CourseCreateSerializer,
    CourseListSerializer,
    CourseSerializer,
    CourseUpdateSerializer,
)
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class CourseViewSet(BaseViewSet, APICodexCourseErrorsMixin):
    serializer_class = CourseSerializer
    permission_classes = [BasicViewPermission]
    queryset = Course.objects.all()
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CourseFilter
    search_fields = ["title"]

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            return CourseListSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        try:
            course = self.get_object()
            serializer = CourseSerializer(
                course, context={"request": request}, many=False
            )
            return Response(serializer.data)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Fant ikke arrangementet"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = CourseCreateSerializer(data=data, context={"request": request})

            if serializer.is_valid():
                course = super().perform_create(serializer)
                serializer = CourseSerializer(
                    course, context={"request": request}, many=False
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                {"detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"detail": "Kunne ikke opprette arrangementet"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            course = self.get_object()
            serializer = CourseUpdateSerializer(
                course, data=request.data, context={"request": request}
            )

            if serializer.is_valid():
                course = super().perform_update(serializer)
                serializer = CourseSerializer(
                    course, context={"request": request}, many=False
                )
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(
                {"detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"detail": "Kunne ikke oppdatere arrangementet"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Kurset ble slettet"}, status=status.HTTP_200_OK)
