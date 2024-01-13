from app.common.viewsets import viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import action
from app.wrapped.serializers.statistics_serializer import StatisticsSerializer
from django.shortcuts import get_object_or_404
from app.common.permissions import BasicViewPermission
from app.wrapped.util.statistics_util import calculate_statistics


class WrappedStatsView(view):
    serializer_class = StatisticsSerializer
    permission_classes = [BasicViewPermission]

    # @action(detail=True, methods=["post"])
    def retrieve(self, request, pk, *args, **kwargs):
        try:
            year = int(pk)
            current_year = datetime.now().year
            if current_year < year:
                return Response(
                    {"detail": "År må være mindre enn eller lik nåværende år"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = request.user

            stats = calculate_statistics(user, year)

            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "Kunne ikke hente ut wrapped-statistikken"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
