from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from app.common.enums import UserClass, UserStudy
from app.common.pagination import BasePagination
from app.common.permissions import IsMember, is_admin_user
from app.content.filters import CheatsheetFilter
from app.content.models import Cheatsheet
from app.content.serializers import CheatsheetSerializer


class CheatsheetViewSet(viewsets.ModelViewSet):
    serializer_class = CheatsheetSerializer
    permission_classes = [IsMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    queryset = Cheatsheet.objects.all()
    pagination_class = BasePagination
    filterset_class = CheatsheetFilter
    search_fields = ["course", "title", "creator"]

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return CheatsheetFilter(self.request.GET, queryset=queryset).qs

    def list(self, request, study, grade):
        try:
            cheatsheet = self.filter_queryset(self.queryset).filter(
                grade=UserClass[grade], study=UserStudy[study]
            )
            page = self.paginate_queryset(cheatsheet)
            if page is not None:
                serializer = CheatsheetSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = CheatsheetSerializer(
                cheatsheet, context={"request": request}, many=True
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cheatsheet.DoesNotExist:
            return Response(
                {"detail": _("Kokeboken eksisterer ikke")},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        if is_admin_user(request):
            serializer = CheatsheetSerializer(data=self.request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"detail": _("Du har ikke tillatelse til å lage en oppskrift")},
            status=status.HTTP_403_FORBIDDEN,
        )

    def update(self, request, study, grade, pk):
        try:
            cheatsheet = self.queryset.get(
                id=pk, grade=UserClass[grade], study=UserStudy[study]
            )
            if is_admin_user(request):
                serializer = CheatsheetSerializer(cheatsheet, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"detail": ("Du har ikke tillatelse til å oppdatere oppskriften")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Cheatsheet.DoesNotExist:
            return Response(
                {"details": _("Oppskriften ble ikke funnet")},
                status=status.HTTP_404_NOT_FOUND,
            )

    def destroy(self, request, study, grade, pk):
        try:
            cheatsheet = self.queryset.get(
                id=pk, grade=UserClass[grade], study=UserStudy[study]
            )
            if is_admin_user(request):
                super().destroy(cheatsheet)
                return Response(
                    {"detail": ("Oppskriften har blitt slettet")},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"detail": ("Ikke riktig tilatelse for å slette en oppskrift")},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Cheatsheet.DoesNotExist:
            return Response(
                {"details": _("Oppskriften ble ikke funnet")},
                status=status.HTTP_404_NOT_FOUND,
            )
