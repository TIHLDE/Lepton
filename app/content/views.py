import os

# Rest Framework
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

# HTTP imports
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Models and serializer imports
from .models import News, Event, \
                    Warning, Category, JobPost, User, UserEvent
from .serializers import NewsSerializer, EventSerializer, \
                         WarningSerializer, CategorySerializer, JobPostSerializer, UserSerializer, UserEventSerializer
from .filters import CHECK_IF_EXPIRED, EventFilter, JobPostFilter

# Permission imports
from .permissions import IsMember, IsDev, IsNoK, IsNoKorPromo

# Pagination imports
from .pagination import BasePagination

# Hash, and other imports
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
import json


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by('-created_at')
    serializer_class = NewsSerializer
    permission_classes = [IsNoK]


class EventViewSet(viewsets.ModelViewSet):
    """
        Display all upcoming events and filter them by title, category and expired
        Excludes expired events by default: to include expired in results, add '&expired=true'
    """
    serializer_class = EventSerializer
    permission_classes = [IsNoKorPromo]
    queryset = Event.objects.filter(start__gte=CHECK_IF_EXPIRED()).order_by('start')
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventFilter
    search_fields = ['title']

    def get_queryset(self):
        if (self.kwargs or 'expired' in self.request.query_params):
            return Event.objects.all().order_by('start')
        return self.queryset

    def update(self, request, pk, *args, **kwargs):
        """ Updates fields passed in request """
        try:
            event = Event.objects.get(pk=pk)
            self.check_object_permissions(self.request, event)
            serializer = EventSerializer(event, data=request.data, partial=True, many=False)

            if serializer.is_valid():
                self.perform_update(serializer)
                return Response({'detail': _('Event successfully updated.')})
            else:
                return Response({'detail': _('Could not perform update')}, status=400)

        except Event.DoesNotExist:
            return Response({'detail': 'Could not find event'}, status=400)


class WarningViewSet(viewsets.ModelViewSet):

    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [IsDev]


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsNoKorPromo]


class JobPostViewSet(viewsets.ModelViewSet):
    """
        Display all upcoming events and filter them by title, category and expired
        Excludes expired events by default: to include expired in search results, add '&expired=true'
    """

    serializer_class = JobPostSerializer
    permission_classes = [IsNoK]
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
    """ API endpoint to display one user """
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
            self.permission_classes = [IsDev, ]
        else:
            self.permission_classes = [IsMember, ]
        return super(UserViewSet, self).get_permissions()

    def get_queryset(self):
        """Returns one application"""
        id = self.request.info['uid'][0]

        try:
            User.objects.get(user_id = id)
        except User.DoesNotExist:
            new_data = {
                'user_id': id,
                'first_name': self.request.info['givenname'][0],
                'last_name': self.request.info['sn'][0],
                'email': self.request.info['mail'][0]
            }
            serializer = UserSerializer(data=new_data)
            print(data)
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
                serializer = UserSerializer(User.objects.get(user_id=pk), context={'request': request}, many=False, data=request.data)
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
    """ Administrate registration, waiting lists and attendance for events """
    serializer_class = UserEventSerializer
    permission_classes = [IsMember]
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
        """ Returns a given user event for the specified event """
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
            user = User.objects.get(user_id=request.info['uid'][0])
        except ObjectDoesNotExist:
            return Response({'detail': _('The provided event and or user does not exist')}, status=404)

        if event.closed:
            return Response({'detail': _('The queue for this event is closed')}, status=400)

        if self.queryset.filter(user=user, event=event).exists():
            return Response({'detail': _('The user event could not be created')}, status=404)

        is_on_wait = (event.limit < event.registered_users_list.all().count() + 1) and event.limit is not 0
        serializer = UserEventSerializer(data=request.data)

        if serializer.is_valid():
            UserEvent(user=user, event=event, is_on_wait=is_on_wait).save()
            return Response({'detail': 'The user event has been created.'})
        else:
            return Response({'detail': serializer.errors}, status=400)

    def update(self, request, event_id, user_id, *args, **kwargs):
        """ Updates fields passed in request """
        try:
            user_event = UserEvent.objects.get(event__pk=event_id, user__user_id=user_id)
            self.check_object_permissions(self.request, user_event)
            serializer = UserEventSerializer(user_event, data=request.data, partial=True, many=False)

            if serializer.is_valid():
                self.perform_update(serializer)
                return Response({'detail': _('User event successfully updated.')})
            else:
                return Response({'detail': _('Could not perform update')}, status=400)

        except UserEvent.DoesNotExist:
            return Response({'detail': 'Could not find user event'}, status=400)

    def destroy(self, request, event_id, user_id):
        """
            Deletes the user event specified with provided event_id and user_id.
        """
        try:
            user_event = UserEvent.objects.get(event__pk=event_id, user__user_id=user_id)
            self.check_object_permissions(request, user_event)
            user_event.delete()
            return Response({'detail': 'User event deleted.'})
        except UserEvent.DoesNotExist:
            return Response({'detail': 'Could not delete user event.'}, status=400)


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

