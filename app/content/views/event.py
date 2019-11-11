from datetime import time

from django.utils.translation import gettext as _

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.response import Response

from ..models import Event
from ..permissions import IsNoKorPromo
from ..serializers import EventSerializer
from ..filters import EventFilter
from ..pagination import BasePagination
from app.util.utils import yesterday


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('{:s} function took {:.3f} ms'.format(f.__name__, (time2-time1)*1000.0))

        return ret
    return wrap


class EventViewSet(viewsets.ModelViewSet):
    """
        Display all upcoming events and filter them by title, category and expired
        Excludes expired events by default: to include expired in results, add '&expired=true'
    """
    serializer_class = EventSerializer
    permission_classes = [IsNoKorPromo]
    queryset = Event.objects.filter(start__gte=yesterday()).order_by('start')
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventFilter
    search_fields = ['title']

    def get_queryset(self):
        if self.kwargs or 'expired' in self.request.query_params:
            return Event.objects.all().order_by('start')
        return Event.objects.filter(start__gte=yesterday()).order_by('start')

    def update(self, request, pk, *args, **kwargs):
        """ Updates fields passed in request """
        try:
            event = Event.objects.get(pk=pk)
            self.check_object_permissions(self.request, event)
            serializer = EventSerializer(event, data=request.data, partial=True, many=False)

            if serializer.is_valid():
                self.perform_update(serializer)
                return Response({'detail': _('Event successfully updated.')})
            else:
                return Response({'detail': _('Could not perform update')}, status=400)

        except Event.DoesNotExist:
            return Response({'detail': 'Could not find event'}, status=400)

