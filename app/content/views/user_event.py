from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from rest_framework import viewsets
from rest_framework.response import Response

from ..models import UserEvent, Event, User
from ..permissions import IsMember, IsAccessingItself, IsDev, IsHS
from ..serializers import UserEventSerializer


class UserEventViewSet(viewsets.ModelViewSet):
    """ Administrates registration, waiting lists and attendance for events """
    serializer_class = UserEventSerializer
    permission_classes = [IsMember, ]
    queryset = UserEvent.objects.all()
    lookup_field = 'user_id'

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            self.permission_classes = [IsAccessingItself | IsHS | IsDev]
        else:
            self.permission_classes = [IsMember, ]
        return super(UserEventViewSet, self).get_permissions()

    def list(self, request, event_id):
        """ Returns all registered users for a given events """
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({'detail': _('Event does not exist.')}, status=404)

        self.check_object_permissions(self.request, event)
        user_event = self.queryset.filter(event__pk=event_id)

        if not user_event.count():
            return Response({'detail': _('No users signed up for this event.')}, status=404)
        serializer = UserEventSerializer(user_event, context={'request': request}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, event_id, user_id):
        """ Returns a registered user for the specified event """
        try:
            user_event = UserEvent.objects.get(event__pk=event_id, user__user_id=user_id)
            serializer = UserEventSerializer(user_event, context={'request': request}, many=False)
            return Response(serializer.data)
        except UserEvent.DoesNotExist:
            return Response({'detail': _('User event not found.')}, status=404)

    def create(self, request, event_id):
        """ Registers a user with the specified event_id and user_id """
        try:
            event = Event.objects.get(pk=event_id)
            user = User.objects.get(user_id=request.info['uid'][0])

            serializer = UserEventSerializer(data=request.data)

            if serializer.is_valid():
                UserEvent(user=user, event=event).save()
                return Response({'detail': 'User event created.'})
            else:
                return Response({'detail': serializer.errors}, status=400)

        except Event.DoesNotExist:
            return Response({'detail': _('The provided event does not exist')}, status=404)
        except User.DoesNotExist:
            return Response({'detail': _('The provided user does not exist')}, status=404)
        except ValidationError as e:
            return Response({'detail': _(e.message)}, status=404)

    def update(self, request, event_id, user_id):
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
        except ValidationError as e:
            return Response({'detail': _(e.message)}, status=404)

    def destroy(self, request, event_id, user_id):
        """ Unregisters the user specified with provided event_id and user_id """
        try:
            user_event = UserEvent.objects.get(event__pk=event_id, user__user_id=user_id)
            self.check_object_permissions(request, user_event)
            user_event.delete()
            return Response({'detail': _('User event deleted.')})
        except UserEvent.DoesNotExist:
            return Response({'detail': _('Could not delete user event.')}, status=400)
