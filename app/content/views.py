from rest_framework import viewsets, mixins, permissions, generics

from .models import Item, News, Event, EventList, Poster, Grid, Image, ImageGallery, Warning
from .serializers import (ItemSerializer, NewsSerializer, EventSerializer,
                          EventListSerializer, PosterSerializer, GridSerializer,
                          ImageSerializer, ImageGallerySerializer, WarningSerializer)
from app.util.models import Gridable

from django.http import HttpResponse

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

def warning(request):
    if request.method == 'POST':

        text = request.POST['text']
        t = request.POST['type']
        warnings = Warning.objects.all()

        if(warnings.count() == 0):
            # Create new warning
            w = Warning(text=text, type=t)
            w.save()

        else:
            # Overwrite existing
            w = warnings.first()
            w.text = text
            w.type = t
            w.save()

        return HTTPResponse(status=200)

    elif request.method == 'DELETE':
        Warning.objects.all().delete()

        return HTTPResponse(status=200)
    
    return HttpResponseNotAllowed(['POST'])