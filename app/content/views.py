import os

# Rest Framework
from rest_framework import viewsets, mixins, permissions, generics, filters
from rest_framework.decorators import api_view, action
from django_filters.rest_framework import DjangoFilterBackend

# HTTP imports
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Models and serializer imports
from .models import News, Event, \
                    Warning, Category, JobPost, User
from .serializers import NewsSerializer, EventSerializer, \
                         WarningSerializer, CategorySerializer, JobPostSerializer, UserSerializer
from .filters import CHECK_IF_EXPIRED, EventFilter, JobPostFilter

# Permission imports
from app.authentication.permissions import IsMemberOrSafe, IsMember, IsHSorDrift, HS_Drift_Promo, HS_Drift_NoK

# Pagination imports
from .pagination import BasePagination

# Hash, and other imports
from django.db.models import Q
import hashlib
import json

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by('-created_at')
    serializer_class = NewsSerializer
    permission_classes = [HS_Drift_Promo]

class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint to display all upcoming events and filter them by title, category and expired
        Excludes expired events by default: to include expired in results, add '&expired=true'
    """
    serializer_class = EventSerializer
    permission_classes = [HS_Drift_Promo]
    queryset = Event.objects.filter(start__gte=CHECK_IF_EXPIRED()).order_by('start')
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventFilter
    search_fields = ['title']

    def get_queryset(self):

        if (self.kwargs or 'expired' in self.request.query_params):
            return Event.objects.all().order_by('start')
        return self.queryset

class WarningViewSet(viewsets.ModelViewSet):

    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [HS_Drift_Promo]

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [HS_Drift_Promo]

class JobPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint to display all upcoming events and filter them by title, category and expired
        Excludes expired events by default: to include expired in search results, add '&expired=true'
    """

    serializer_class = JobPostSerializer
    permission_classes = [HS_Drift_NoK]
    pagination_class = BasePagination

    queryset = JobPost.objects.filter(deadline__gte=CHECK_IF_EXPIRED()).order_by('deadline')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = JobPostFilter
    search_fields = ['title', 'company']

    def get_queryset(self):
        if (self.kwargs or 'expired' in self.request.query_params):
            return JobPost.objects.all().order_by('deadline')
        return self.queryset




class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint to display one user'
    """
    serializer_class = UserSerializer
    permission_classes = [IsMember]
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    def get_permissions(self):
        # Your logic should be all here
        if self.request.method == 'POST':
            self.permission_classes = [IsHSorDrift, ]
        else:
            self.permission_classes = [IsMember, ]
        return super(UserViewSet, self).get_permissions()

    def get_queryset(self):
        """Returns one application"""
        id = self.request.user_id

        try:
            User.objects.get(user_id = id)
        except User.DoesNotExist:
            new_data = {
                'user_id': id,
                'first_name': self.request.first_name,
                'last_name': self.request.last_name,
                'email': self.request.email
            }
            serializer = UserSerializer(data=new_data)
            if serializer.is_valid():
                serializer.save()
        return self.queryset.filter(user_id = id)

    def perform_create(self, serializer):
        serializer = UserSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save()

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

