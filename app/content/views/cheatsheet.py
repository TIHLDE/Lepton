from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.enums import NativeUserStudy as UserStudy
from app.common.enums import get_user_class_name
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission, is_admin_user
from app.common.viewsets import BaseViewSet
from app.content.filters import CheatsheetFilter
from app.content.models import Cheatsheet
from app.content.serializers import CheatsheetSerializer


class CheatsheetViewSet(BaseViewSet):
    serializer_class = CheatsheetSerializer
    permission_classes = [BasicViewPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    queryset = Cheatsheet.objects.all()
    pagination_class = BasePagination
    filterset_class = CheatsheetFilter
    search_fields = ["course", "title", "creator"]

    def get_object(self):
        if "pk" not in self.kwargs:
            grade = get_user_class_name(int(self.kwargs["grade"]))
            return self.filter_queryset(self.queryset).filter(
                grade=grade,
                study=UserStudy[self.kwargs["study"]],
            )

        return super().get_object()

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return CheatsheetFilter(self.request.GET, queryset=queryset).qs

    def list(self, request, *args, **kwargs):
        """Return a list of cheatsheets filtered by UserClass and UserStudy"""
        try:
            cheatsheet = self.get_object()
            page = self.paginate_queryset(cheatsheet)
            if page is not None:
                serializer = CheatsheetSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = CheatsheetSerializer(
                cheatsheet, context={"request": request}, many=True
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cheatsheet.DoesNotExist as cheatsheet_not_exist:
            capture_exception(cheatsheet_not_exist)
            return Response(
                {"detail": "Kokeboken eksisterer ikke"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        """Creates a new cheatsheet"""
        if is_admin_user(request):
            serializer = CheatsheetSerializer(
                data=self.request.data, context={"request": request}
            )
            if serializer.is_valid():
                super().perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"detail": "Du har ikke tillatelse til å lage en oppskrift"},
            status=status.HTTP_403_FORBIDDEN,
        )

    def update(self, request, *args, **kwargs):
        """Updates a cheatsheet retrieved by UserClass and UserStudy and pk"""
        try:
            cheatsheet = self.get_object()
            if is_admin_user(request):
                serializer = CheatsheetSerializer(
                    cheatsheet, data=request.data, context={"request": request}
                )
                if serializer.is_valid():
                    super().perform_update(serializer)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"detail": "Du har ikke tillatelse til å oppdatere oppskriften"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Cheatsheet.DoesNotExist as cheatsheet_not_exist:
            capture_exception(cheatsheet_not_exist)
            return Response(
                {"details": "Oppskriften ble ikke funnet"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def destroy(self, request, *args, **kwargs):
        """Deletes a cheatsheet retrieved by UserClass and UserStudy"""
        try:
            if is_admin_user(request):
                super().destroy(request, *args, **kwargs)
                return Response(
                    {"detail": "Oppskriften har blitt slettet"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"detail": "Du har ikke riktig tilatelser for å slette en oppskrift"},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Cheatsheet.DoesNotExist as cheatsheet_not_exist:
            capture_exception(cheatsheet_not_exist)
            return Response(
                {"details": "Oppskriften ble ikke funnet"},
                status=status.HTTP_404_NOT_FOUND,
            )
