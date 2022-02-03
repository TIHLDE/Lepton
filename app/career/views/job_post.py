from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response

from app.career.filters.job_post import JobPostFilter
from app.career.models.job_post import JobPost
from app.career.serializers.job_post import JobPostSerializer
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.util.utils import yesterday


class JobPostViewSet(BaseViewSet):
    """
        Display all not expired jobposts and filter them by title and expired
        Excludes expired jobposts by default: to include expired in search results, add '&expired=true'
    """

    serializer_class = JobPostSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination
    queryset = JobPost.objects.filter(deadline__gte=yesterday()).order_by("deadline")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = JobPostFilter
    search_fields = ["title", "company"]

    def get_queryset(self):
        if self.kwargs or "expired" in self.request.query_params:
            return JobPost.objects.all().order_by("deadline")
        return JobPost.objects.filter(deadline__gte=yesterday()).order_by("deadline")

    def destroy(self, request, *args, **kwargs):
        """ Delete the jobpost """
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Jobbannonsen ble slettet"}, status=status.HTTP_200_OK
        )
