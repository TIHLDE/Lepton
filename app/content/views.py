from rest_framework import viewsets, mixins, permissions, generics

# HTTP imports
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Models and serializer imports
from .models import Item, News, Event, EventList, Poster, Image, \
                    ImageGallery, Warning, Category, JobPost
from .serializers import ItemSerializer, NewsSerializer, EventSerializer, \
                         EventListSerializer, PosterSerializer, \
                         ImageSerializer, \
                         ImageGallerySerializer, WarningSerializer, CategorySerializer, JobPostSerializer
from app.util.models import Gridable

# Permission imports
from app.authentication.permissions import IsMemberOrSafe, IsHSorDrift, HS_Drift_Promo, HS_Drift_NoK

# Datetime, hash, and other imports
from datetime import datetime, timedelta
from django.db.models import Q
import hashlib
import json

class ItemViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Item.objects.all().select_related(
        'news',
        'eventlist',
        'poster',
        'imagegallery').order_by('order', '-created_at')
    serializer_class = ItemSerializer


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by('-created_at')
    serializer_class = NewsSerializer
    permission_classes = [HS_Drift_Promo]


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [HS_Drift_Promo]

    def get_queryset(self):
        queryset = Event.objects.all()

        if self.request.method == 'GET' and 'newest' in self.request.GET:
            # Returns the newest events ordered by 'start'
            return Event.objects.filter(start__gte=datetime.now()-timedelta(days=1)).order_by('start')
        elif self.request.method == 'GET' and 'category' in self.request.GET:
            # Returns events by category ordered by 'start'
            return Event.objects.filter(category=self.request.GET.get('category')).order_by('start')[:25]
        elif self.request.method == 'GET' and 'search' in self.request.GET:
            # Returns events matching a search word, ordered by 'start'
            return Event.objects.filter(Q(title__istartswith=self.request.GET.get('search')) | Q(title__icontains=self.request.GET.get('search'))).order_by('start')[:25]
        elif self.request.method == 'GET' and 'expired' in self.request.GET:
            # Returns events that is expired, ordered by 'start'
            return Event.objects.filter(start__lte=datetime.now()-timedelta(days=1)).order_by('start')[:25]

        return queryset


class EventListViewSet(viewsets.ModelViewSet):
    queryset = EventList.objects.all()
    serializer_class = EventListSerializer
    permission_classes = [IsMemberOrSafe]


class PosterViewSet(viewsets.ModelViewSet):
    queryset = Poster.objects.all()
    serializer_class = PosterSerializer
    permission_classes = [HS_Drift_Promo]

class ImageGalleryViewSet(viewsets.ModelViewSet):
    queryset = ImageGallery.objects.all()
    serializer_class = ImageGallerySerializer
    permission_classes = [HS_Drift_Promo]


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [HS_Drift_Promo]

class WarningViewSet(viewsets.ModelViewSet):

    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [HS_Drift_Promo]

class JobPostViewSet(viewsets.ModelViewSet):

    serializer_class = JobPostSerializer
    permission_classes = [HS_Drift_NoK]

    def get_queryset(self):
        queryset = JobPost.objects.all()

        if self.request.method == 'GET' and 'newest' in self.request.GET:
            # Returns the newest job posts ordered by deadline
            return JobPost.objects.filter(deadline__gte=datetime.now()-timedelta(days=1)).order_by('deadline')[:25]
        elif self.request.method == 'GET' and 'search' in self.request.GET:
            # Returns job posts matching a search word, ordered by deadline
            return JobPost.objects.filter(Q(title__icontains=self.request.GET.get('search')) | Q(company__icontains=self.request.GET.get('search'))).order_by('deadline')[:25]
        elif self.request.method == 'GET' and 'expired' in self.request.GET:
            # Returns expired job posts, ordered by deadline
            return JobPost.objects.filter(deadline__lte=datetime.now()-timedelta(days=1)).order_by('deadline')[:25]

        return queryset


# Method for accepting company interest forms from the company page

from django.core.mail import send_mail

@csrf_exempt
def accept_form(request):
    if request.method == 'POST':
        try:
            #Get body from request
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)

            #Define mail content
            sent_from = 'no-reply@tihlde.org'
            to = 'orakel@tihlde.org'
            subject = body["info"]['bedrift'] + " vil ha " + ", ".join(body["type"][:-2] + [" og ".join(body["type"][-2:])]) + " i " + ", ".join(body["time"][:-2] + [" og ".join(body["time"][-2:])])
            email_body = """\
Bedrift-navn:
%s

Kontaktperson:
navn: %s
epost: %s

Valgt semester:
%s

Valg arrangement:
%s

Kommentar:
%s
            """ % (body["info"]["bedrift"], body["info"]["kontaktperson"], body["info"]["epost"], ", ".join(body["time"]), ", ".join(body["type"]), body["comment"])

            send_mail(
                subject,
                email_body,
                sent_from,
                [to],
                fail_silently = False
            )

            return JsonResponse({})

        except:
            print('Something went wrong...')
            raise
            #return HttpResponse(status = 500)

