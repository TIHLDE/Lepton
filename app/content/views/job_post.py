from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from ..models import JobPost
from ..serializers import JobPostSerializer
from ..permissions import IsNoK
from ..filters import JobPostFilter
from ..pagination import BasePagination
from app.util.utils import yesterday



class JobPostViewSet(viewsets.ModelViewSet):
    """
        Display all upcoming events and filter them by title, category and expired
        Excludes expired events by default: to include expired in search results, add '&expired=true'
    """

    serializer_class = JobPostSerializer
    permission_classes = [IsNoK]
    pagination_class = BasePagination
    queryset = JobPost.objects.filter(deadline__gte=yesterday()).order_by('deadline')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = JobPostFilter
    search_fields = ['title', 'company']

    def get_queryset(self):
        if self.kwargs or 'expired' in self.request.query_params:
            return JobPost.objects.all().order_by('deadline')
        return JobPost.objects.filter(deadline__gte=yesterday()).order_by('deadline')
