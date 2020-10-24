from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.response import Response

from app.util.utils import yesterday

from ..filters import JobPostFilter
from ..models import JobPost
from ..pagination import BasePagination
from ..permissions import IsDev, IsNoK
from ..serializers import JobPostSerializer


class JobPostViewSet(viewsets.ModelViewSet):
    """
        Display all not expired jobposts and filter them by title and expired
        Excludes expired jobposts by default: to include expired in search results, add '&expired=true'
    """

    serializer_class = JobPostSerializer
    permission_classes = [IsDev | IsNoK]
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
        return Response({"detail": _("Jobbannonsen ble slettet")}, status=200)
