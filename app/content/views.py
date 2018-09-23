from rest_framework import viewsets, mixins, permissions, generics
from rest_framework.views import APIView

from .models import Item, News, Event, EventList, Poster, Grid, Image, ImageGallery, Warning
from .serializers import (ItemSerializer, NewsSerializer, EventSerializer,
                          EventListSerializer, PosterSerializer, GridSerializer,
                          ImageSerializer, ImageGallerySerializer, WarningSerializer)
from app.util.models import Gridable

from django.http import HttpResponse, HttpResponseNotAllowed

class ItemViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Item.objects.all().select_related('news', 'eventlist', 'poster', 'imagegallery').order_by('order')
    serializer_class = ItemSerializer

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    # permission_classes = [permissions.IsAdminUser]

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # permission_classes = [permissions.IsAdminUser]

class EventListViewSet(viewsets.ModelViewSet):
    queryset = EventList.objects.all()
    serializer_class = EventListSerializer
    # permission_classes = [permissions.IsAdminUser]

class PosterViewSet(viewsets.ModelViewSet):
    queryset = Poster.objects.all()
    serializer_class = PosterSerializer
    permission_classes = [permissions.IsAdminUser]

class GridViewSet(viewsets.ModelViewSet):
    queryset = Grid.objects.all()
    serializer_class = GridSerializer
    #permission_classes = [permissions.IsAdminUser]

class ImageGalleryViewSet(viewsets.ModelViewSet):
    queryset = ImageGallery.objects.all()
    serializer_class = ImageGallerySerializer
    permission_classes = [permissions.IsAdminUser]

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAdminUser]

class WarningViewSet(APIView):

    queryset = Warning.objects.all()
    serializer_class = WarningSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, format=None):
        warnings = Warning.objects.all()
        serializer = WarningSerializer()
        return HttpResponse(content=warnings, status=200)

    def post(self, request, format=None):

        
        serializer = WarningSerializer(data=request.data)

        if serializer.is_valid():
            text = serializer.data.get('text')
            t = serializer.data.get('type')

            if Warning.objects.count() == 0:
                # Create new warning
                w = Warning(text=text, type=t)
                w.save()

            else:
                # Overwrite existing
                w = Warning.objects.first()
                w.text = text
                w.type = t
                w.save()
            
            return HttpResponse(status=200)
        return HttpResponse(status=400)
       

    def delete(self, request, format=None):
        Warning.objects.all().delete()

        return HttpResponse(status=200)
