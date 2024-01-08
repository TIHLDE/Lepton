from app.common.viewsets import BaseViewSet
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action
from app.wrapped.serializers.statistics_serializer import (
    StatisticsGetSerializer,
    StatisticsSerializer,
)
from django.shortcuts import get_object_or_404
from app.common.permissions import BasicViewPermission


class WrappedStatsView(BaseViewSet):
    serializer_class = [StatisticsSerializer]

    # @action(detail=True, methods=["post"])
    def retrieve(self, request, *args, **kwargs):
        data = request.data
        serializer = StatisticsGetSerializer(data=data)
        if serializer.is_valid():
            super().perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": "Fant ikke wrapped-statistikken."},
            status=status.HTTP_404_NOT_FOUND,
        )
