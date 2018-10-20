from rest_framework import viewsets, mixins, permissions, generics

from .models import Item, News, Event, EventList, Poster, Grid, Image, \
                    ImageGallery, Warning, Category
from .serializers import ItemSerializer, NewsSerializer, EventSerializer, \
                         EventListSerializer, PosterSerializer, \
                         GridSerializer, ImageSerializer, \
                         ImageGallerySerializer, WarningSerializer, CategorySerializer
from app.util.models import Gridable

from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse

from datetime import datetime, timedelta
from django.db.models import Q  


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
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()

        if self.request.method == 'GET' and 'newest' in self.request.GET:
            return Event.objects.filter(start__gte=datetime.now()-timedelta(days=1)).order_by('start')
        elif self.request.method == 'GET' and 'search' in self.request.GET:
            return Event.objects.filter(Q(title__istartswith=self.request.GET.get('search')) | Q(title__icontains=self.request.GET.get('search'))).order_by('start')[:25]
        elif self.request.method == 'GET' and 'expired' in self.request.GET:
            return Event.objects.filter(start__lte=datetime.now()-timedelta(days=1)).order_by('start')[:25]

        return queryset


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

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

