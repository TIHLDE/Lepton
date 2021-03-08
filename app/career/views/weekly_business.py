from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import status, viewsets
from rest_framework.response import Response

from app.career.models import WeeklyBusiness
from app.career.serializers import WeeklyBusinessSerializer
from app.common.drive_handler import upload_and_replace_image_with_cloud_link
from app.common.enums import AppModel
from app.common.pagination import BasePagination
from app.common.permissions import IsNoK
from app.util import today, week_nr


class WeeklyBusinessViewSet(viewsets.ModelViewSet):

    queryset = WeeklyBusiness.objects.none()
    serializer_class = WeeklyBusinessSerializer
    permission_classes = [IsNoK]
    pagination_class = BasePagination

    def get_queryset(self):
        """
        Return all non-expired weekly_business by default.
        Filter expired events based on url query parameter.
        """
        if "expired" in self.request.query_params:
            return WeeklyBusiness.objects.all().order_by("year", "week")
        if "this_week" in self.request.query_params:
            return WeeklyBusiness.objects.filter(
                year=today().year, week=week_nr(today())
            )
        in_future_this_year_filter = Q(year=today().year) & Q(
            week__gte=week_nr(today())
        )
        next_year_filter = Q(year__gt=today().year)
        return WeeklyBusiness.objects.filter(
            (in_future_this_year_filter) | next_year_filter
        ).order_by("year", "week")

    def list(self, request, *args, **kwargs):
        weekly_business = self.get_queryset()
        page = self.paginate_queryset(weekly_business)
        if page is not None:
            serializer = WeeklyBusinessSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = WeeklyBusinessSerializer(
            weekly_business, context={"request": request}, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            upload_and_replace_image_with_cloud_link(request, AppModel.WEEKLY_BUSINESS)

            serializer = WeeklyBusinessSerializer(data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as value_error:
            return Response(
                {"detail": str(value_error)}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, pk):
        weekly_business = get_object_or_404(WeeklyBusiness, id=pk)
        self.check_object_permissions(self.request, weekly_business)
        upload_and_replace_image_with_cloud_link(request, AppModel.WEEKLY_BUSINESS)
        serializer = WeeklyBusinessSerializer(
            weekly_business, data=request.data, partial=True
        )
        try:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as value_error:
            return Response(
                {"detail": str(value_error)}, status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Ukens bedrift ble slettet"}, status=status.HTTP_200_OK
        )
