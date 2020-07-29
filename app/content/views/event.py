from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.response import Response

from ..models import Event
from ..serializers import EventListSerializer, EventSerializer, EventAdminSerializer, EventCreateUpdateSerializer
from ..permissions import IsNoKorPromo, is_admin_user
from ..filters import EventFilter
from ..pagination import BasePagination
from app.util import yesterday

import json


class EventViewSet(viewsets.ModelViewSet):
    """
        Display all upcoming events and filter them by title, category and expired
        Excludes expired events by default: to include expired in results, add '&expired=true'
    """
    serializer_class = EventListSerializer
    permission_classes = [IsNoKorPromo]
    queryset = Event.objects.filter(start_date__gte=yesterday()).order_by('start_date')
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventFilter
    search_fields = ['title']

    def get_queryset(self):
        if self.kwargs or 'expired' in self.request.query_params:
            return Event.objects.all().order_by('start_date')
        return Event.objects.filter(start_date__gte=yesterday()).order_by('start_date')

    def retrieve(self, request, pk):
        """ Returns a registered user for the specified event """
        try:
            event = Event.objects.get(pk=pk)
            if is_admin_user(request):
                serializer = EventAdminSerializer(event, context={'request': request}, many=False)
            else:
                serializer = EventSerializer(event, context={'request': request}, many=False)
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response({'detail': _('User event not found.')}, status=404)


    def update(self, request, pk):
        """ Updates fields passed in request """
        try:
            event = Event.objects.get(pk=pk)
            self.check_object_permissions(self.request, event)
            serializer = EventCreateUpdateSerializer(event, data=request.data, partial=True)

            if serializer.is_valid():
                save = serializer.save()
                return Response({'detail': _('Event successfully updated.'), 'id': save.id}, status=200)
            else:
                return Response({'detail': _('Could not perform update')}, status=400)

        except Event.DoesNotExist:
            return Response({'detail': 'Could not find event'}, status=400)

        except Exception as e:
            return Response({'detail': e}, status=400)

    def create(self, request, *args, **kwargs):
        try:
            serializer = EventCreateUpdateSerializer(data=request.data)

            if serializer.is_valid():
                save = serializer.save()
                return Response({'detail': 'Event created', 'id': save.id}, status=201)
            else:
                return Response({'detail': serializer.errors}, status=400)
        except ValidationError as e:
            return Response({'detail': _(e)}, status=400)
