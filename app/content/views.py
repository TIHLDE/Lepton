import os

# Rest Framework
from rest_framework import viewsets, mixins, permissions, generics, filters
from rest_framework.decorators import api_view, action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

# HTTP imports
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Models and serializer imports
from .models import News, Event, \
                    Warning, Category, JobPost, User, UserEvent
from .serializers import NewsSerializer, EventSerializer, \
                         WarningSerializer, CategorySerializer, JobPostSerializer, UserSerializer, UserEventSerializer, UserMemberSerializer
from .filters import CHECK_IF_EXPIRED, EventFilter, JobPostFilter

# Permission imports
from app.authentication.permissions import IsMemberOrSafe, IsMember, IsHSorDrift, HS_Drift_Promo, HS_Drift_NoK

# Pagination imports
from .pagination import BasePagination

# Hash, and other imports
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
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
        
        TODO:
            - Legg til funksjonalitet for påmelding
                - legg til en add_user_to_list som kaller på UserEventViewSet.create med
                    event_id og user_id 
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
    API endpoint to display one user
    """
    serializer_class = UserSerializer
    permission_classes = [IsMember]
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    def get_object(self):
        user = self.request.user_id
        return self.queryset.filter(user_id = user)

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

    def update(self, request, pk, *args, **kwargs):
        """ Updates fields passed in request """
        try:
            self.check_object_permissions(self.request, User.objects.get(user_id=pk))
            if self.request.user_id == pk:
                serializer = UserMemberSerializer(User.objects.get(user_id=pk), context={'request': request}, many=False, data=request.data)
                if serializer.is_valid():
                    self.perform_update(serializer)
                    return Response({'detail': _('User successfully updated.')})
                else:
                    return Response({'detail': _('Could not perform user update')}, status=400)
            else:
                return Response({'detail': _('Not authenticated to perform user update')}, status=400)
        except ObjectDoesNotExist:
            return Response({'detail': 'Could not find user'}, status=400)



class UserEventViewSet(viewsets.ModelViewSet):
    """
        API endpoint to display all users signed up to an event
            TODO: object should be created when user signes up to an event - done at frontend?
    """
    serializer_class = UserEventSerializer
    permission_classes = [HS_Drift_NoK]
    queryset = UserEvent.objects.all()
    lookup_field = 'user_id' 

    def list(self, request, event_id):
        """ Returns all user events for given event """
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({'detail': _('The event does not exist.')}, status=404)
        self.check_object_permissions(self.request, event)
        user_event = self.queryset.filter(event__pk=event_id)
        if not user_event.count():
            return Response({'detail': _('No users signed up for this event.')}, status=404)
        serializer = UserEventSerializer(user_event, context={'request': request}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, event_id, user_id):
        """Returns a given user event for the specified event """
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({'detail': _('The user event does not exist.')}, status=404)
        self.check_object_permissions(self.request, event)
        try:
            user_event = UserEvent.objects.get(event__pk=event_id, user__user_id=user_id)
            serializer = UserEventSerializer(user_event, context={'request': request}, many=False)
            return Response(serializer.data)
        except UserEvent.DoesNotExist:
            return Response({'detail': _('The user event has not been found.')}, status=404)


    def create(self, request, event_id):
        """ Creates a new user-event with the specified event_id and user_id """
        try:
            event = Event.objects.get(pk=event_id)
            user = User.objects.get(user_id=request.data['user_id']) # or user object or email?
        except ObjectDoesNotExist:
            return Response({'detail': _('The provided event and or user does not exist')}, status=404)

        if  self.queryset.filter(user=user, event=event).exists():
            return Response({'detail': _('The user event could not be created')}, status=404)

        is_on_wait = (event.limit < event.registered_users_list.all().count() + 1) and event.limit is not 0
        serializer = UserEventSerializer(data=request.data)
        if serializer.is_valid():
            UserEvent(user=user, event=event, is_on_wait=is_on_wait).save()
            return Response({'detail': 'The user event has been created.'})
        else:
            return Response({'detail': serializer.errors}, status=400)

    def update(self, request, *args, **kwargs):
        """ Updates fields passed in request """
        try:
            self.check_object_permissions(self.request, self.get_object())
            serializer = UserEventSerializer(self.get_object(), context={'request': request}, many=False, data=request.data)
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response({'detail': _('User event successfully updated.')})
            else:
                return Response({'detail': _('Could not perform update')}, status=400)
        except ObjectDoesNotExist:
            return Response({'detail': 'Could not find event'}, status=400)

    def destroy(self, request, event_id, user_id):
        pass


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

