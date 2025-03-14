from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from app.career.models import WeeklyBusiness
from app.career.serializers import WeeklyBusinessSerializer
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.util import now, week_nr


class WeeklyBusinessViewSet(BaseViewSet):
    queryset = WeeklyBusiness.objects.none()
    serializer_class = WeeklyBusinessSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_queryset(self):
        """
        Return all non-expired weekly_business by default.
        Filter expired events based on url query parameter.
        """
        if "expired" in self.request.query_params:
            return WeeklyBusiness.objects.all().order_by("year", "week")
        if "this_week" in self.request.query_params:
            return WeeklyBusiness.objects.filter(year=now().year, week=week_nr(now()))
        in_future_this_year_filter = Q(year=now().year) & Q(week__gte=week_nr(now()))
        next_year_filter = Q(year__gt=now().year)
        return WeeklyBusiness.objects.filter(
            in_future_this_year_filter | next_year_filter
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
            serializer = WeeklyBusinessSerializer(
                data=request.data, partial=True, context={"request": request}
            )

            if serializer.is_valid():
                super().perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError:
            return Response(
                {"detail": "En feil oppstod under behandlingen av forespørselen."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, pk):
        weekly_business = get_object_or_404(WeeklyBusiness, id=pk)
        self.check_object_permissions(self.request, weekly_business)
        serializer = WeeklyBusinessSerializer(
            weekly_business,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        try:
            if serializer.is_valid():
                super().perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError:
            return Response(
                {"detail": "En feil oppstod under behandlingen av forespørselen."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Ukens bedrift ble slettet"}, status=status.HTTP_200_OK
        )
