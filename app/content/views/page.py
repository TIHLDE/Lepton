from django.core.exceptions import MultipleObjectsReturned
from django.utils.translation import gettext as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.permissions import IsDev, IsHS
from app.content.models import Page
from app.content.serializers import PageSerializer, PageTreeSerializer


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [IsDev | IsHS]
    lookup_url_kwarg = "path"
    lookup_value_regex = ".*"

    def get_page_from_tree(self):
        return Page.get_by_path(self.kwargs["path"])

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = []
        return super(PageViewSet, self).get_permissions()

    def retrieve(self, request, *args, **kwargs):
        try:
            page = self.get_page_from_tree()
            serializer = PageSerializer(page, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Page.DoesNotExist:
            return Response(
                {"detail": _("Fant ikke siden")}, status=status.HTTP_404_NOT_FOUND
            )
        except MultipleObjectsReturned as tree_destroyed_error:
            capture_exception(tree_destroyed_error)
            return Response(
                {"detail": _("Kan ikke hente siden fordi treet er ødelagt")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        try:
            page = self.queryset.get(parent=None)
            serializer = PageSerializer(page, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Page.DoesNotExist:
            return Response(
                {"detail": _("Fant ikke siden")}, status=status.HTTP_404_NOT_FOUND
            )
        except MultipleObjectsReturned as tree_destroyed_error:
            capture_exception(tree_destroyed_error)
            return Response(
                {"detail": _("Kan ikke hente siden fordi treet er ødelagt")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create(self, request, *args, **kwargs):
        try:
            parent = Page.get_by_path(request.data["path"])
            page = Page(parent=parent)
            serializer = PageSerializer(page, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {
                    "detail": _(
                        "En annen side med dette navnet eksisterer allerede i denne mappen"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Page.DoesNotExist:
            return Response(
                {"detail": _("Fant ikke siden")}, status=status.HTTP_404_NOT_FOUND
            )
        except MultipleObjectsReturned as tree_destroyed_error:
            capture_exception(tree_destroyed_error)
            return Response(
                {"detail": _("Kan ikke lage siden fordi treet er ødelagt")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        try:
            page = self.get_page_from_tree()
            page.parent = Page.get_by_path(request.data["path"])
            serializer = PageSerializer(page, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except Page.DoesNotExist:
            return Response(
                {"detail": _("Fant ikke siden")}, status=status.HTTP_404_NOT_FOUND
            )
        except MultipleObjectsReturned as tree_destroyed_error:
            capture_exception(tree_destroyed_error)
            return Response(
                {"detail": _("Kan ikke endre siden fordi treet er ødelagt")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        if "path" not in kwargs:
            return Response(
                {"detail": _("Urlen må innholde referanse til side treet")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            page = self.get_page_from_tree()
            if len(page.get_children()) > 0:
                return Response(
                    {
                        "detail": _(
                            "Du kan ikke slette en side som har undersider, slett eller flytt undersidene først"
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            self.perform_destroy(page)
            return Response(
                {"detail": _("Siden ble slettet")}, status=status.HTTP_200_OK,
            )
        except Page.DoesNotExist:
            return Response(
                {"detail": _("Fant ikke siden")}, status=status.HTTP_404_NOT_FOUND
            )
        except MultipleObjectsReturned as tree_destroyed_error:
            capture_exception(tree_destroyed_error)
            return Response(
                {"detail": _("Kan ikke slette siden fordi treet er ødelagt")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def tree(self, request, *args, **kwargs):
        root = Page.objects.get(parent=None)
        serializer = PageTreeSerializer(root)
        return Response(serializer.data, status=status.HTTP_200_OK)
