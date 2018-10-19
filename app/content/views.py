from rest_framework import viewsets, mixins, permissions, generics

from .models import Item, News, Event, EventList, Poster, Grid, Image, \
                    ImageGallery, Warning
from .serializers import ItemSerializer, NewsSerializer, EventSerializer, \
                         EventListSerializer, PosterSerializer, \
                         GridSerializer, ImageSerializer, \
                         ImageGallerySerializer, WarningSerializer
from app.util.models import Gridable

from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse

from datetime import datetime, timedelta


class ItemViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Item.objects.all().select_related(
        'news',
        'eventlist',
        'poster',
        'imagegallery').order_by('order')
    serializer_class = ItemSerializer


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().filter(start=datetime.now()-timedelta(days=1)).order_by('-start')
    serializer_class = EventSerializer


class EventListViewSet(viewsets.ModelViewSet):
    queryset = EventList.objects.all()
    serializer_class = EventListSerializer


class PosterViewSet(viewsets.ModelViewSet):
    queryset = Poster.objects.all()
    serializer_class = PosterSerializer
    permission_classes = [permissions.IsAdminUser]


class GridViewSet(viewsets.ModelViewSet):
    queryset = Grid.objects.all()
    serializer_class = GridSerializer


class ImageGalleryViewSet(viewsets.ModelViewSet):
    queryset = ImageGallery.objects.all()
    serializer_class = ImageGallerySerializer
    permission_classes = [permissions.IsAdminUser]


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAdminUser]


class WarningViewSet(viewsets.ModelViewSet):

    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

