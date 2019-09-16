from rest_framework import viewsets, mixins, permissions, generics
import os
from rest_framework.decorators import api_view

# HTTP imports
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Models and serializer imports
from .models import News, Event, \
                    Warning, Category, JobPost
from .serializers import NewsSerializer, EventSerializer, \
                         WarningSerializer, CategorySerializer, JobPostSerializer
from app.util.models import Gridable

# Permission imports
from app.authentication.permissions import IsMemberOrSafe, IsHSorDrift, HS_Drift_Promo, HS_Drift_NoK

# Pagination imports
from .pagination import TwentyFivePagination

# Datetime, hash, and other imports
from datetime import datetime, timedelta
from django.db.models import Q
import hashlib
import json

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by('-created_at')
    serializer_class = NewsSerializer
    permission_classes = [HS_Drift_Promo]

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [HS_Drift_Promo]
    pagination_class = TwentyFivePagination

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

class WarningViewSet(viewsets.ModelViewSet):

    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [HS_Drift_Promo]

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [HS_Drift_Promo]

class JobPostViewSet(viewsets.ModelViewSet):

    serializer_class = JobPostSerializer
    permission_classes = [HS_Drift_NoK]
    pagination_class = TwentyFivePagination

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
# TODO: MOVE TO TEMPLATE
from django.core.mail import send_mail

@csrf_exempt
@api_view(['POST'])
def accept_form(request):
    try:
        #Get body from request
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        #Define mail content
        sent_from = 'no-reply@tihlde.org'
        to = os.environ.get('EMAIL_RECEIVER') or 'orakel@tihlde.org'
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

        numOfSentMails = send_mail(
            subject,
            email_body,
            sent_from,
            [to],
            fail_silently = False
        )
        return JsonResponse({}, status= 200 if numOfSentMails > 0 else 500)

    except:
        print('Something went wrong...')
        raise
        #return HttpResponse(status = 500)

