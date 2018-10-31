from rest_framework import viewsets, mixins, permissions, generics

from .models import Item, News, Event, EventList, Poster, Grid, Image, \
                    ImageGallery, Warning, Category, JobPost
from .serializers import ItemSerializer, NewsSerializer, EventSerializer, \
                         EventListSerializer, PosterSerializer, \
                         GridSerializer, ImageSerializer, \
                         ImageGallerySerializer, WarningSerializer, CategorySerializer, JobPostSerializer
from app.util.models import Gridable

from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta
from django.db.models import Q  

import hashlib
import json

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
        elif self.request.method == 'GET' and 'category' in self.request.GET:
            return Event.objects.filter(category=self.request.GET.get('category')).order_by('start')[:25]
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

class JobPostViewSet(viewsets.ModelViewSet):

    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer


@csrf_exempt
def auth_password(request):
    
    if request.method == 'POST':
        # Retrieve password from body
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        password = body['password']

        # Hash password
        hash_object = hashlib.sha256(str(password).strip('\n ').encode())
        hashedPassword = hash_object.hexdigest()

        # Evaluate password
        realPassword = "3216f62cf30ce48c631f87ba5147f3fc3b1c1c87f8f3f416e568a917f6b9298d"
        authenticated = hashedPassword == realPassword
        data = {
            'authenticated': authenticated,
        }
        return JsonResponse(data)

    # Method is not allowed
    return HttpResponseNotAllowed(['POST'])
