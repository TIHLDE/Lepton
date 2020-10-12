from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import viewsets
from rest_framework.response import Response

from app.util.utils import today

from ...util.mailer import send_registration_mail
from ..models import Event, Registration, User
from ..permissions import RegistrationPermission, is_admin_user
from ..serializers import RegistrationSerializer


class RegistrationViewSet(viewsets.ModelViewSet):
    """ Administrates registration, waiting lists and attendance for events """

    serializer_class = RegistrationSerializer
    permission_classes = [RegistrationPermission]
    queryset = Registration.objects.all()
    lookup_field = "user_id"

    def list(self, request, event_id):
        """ Returns all registered users for a given events """
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({"detail": _("Event does not exist.")}, status=404)

        self.check_object_permissions(self.request, event)
        registration = self.queryset.filter(event__pk=event_id)

        serializer = RegistrationSerializer(
            registration, context={"request": request}, many=True
        )
        return Response(serializer.data)

    def retrieve(self, request, event_id, user_id):
        """ Returns a registered user for the specified event """
        current_user_id = request.id
        if user_id != current_user_id:
            return Response(
                {"detail": _("Cannot access the registration for this user")},
                status=400,
            )

        try:
            registration = Registration.objects.get(
                event__pk=event_id, user__user_id=current_user_id
            )
            serializer = RegistrationSerializer(
                registration, context={"request": request}, many=False
            )
            return Response(serializer.data, status=200)
        except Registration.DoesNotExist:
            return Response({"detail": _("Registration not found.")}, status=404)

    def create(self, request, event_id):
        """ Registers a user with the specified event_id and user_id """
        try:
            event = Event.objects.get(pk=event_id)
            user = User.objects.get(user_id=request.id)
            serializer = RegistrationSerializer(data=request.data)
            if serializer.is_valid():
                Registration(user=user, event=event).save()
                return Response({"detail": "Registration created."}, status=200)
            else:
                return Response({"detail": serializer.errors}, status=400)

        except Event.DoesNotExist:
            msg = _("The provided event does not exist")

        except User.DoesNotExist:
            msg = _("The provided user does not exist")

        except ValidationError as e:
            msg = _(e.message)

        return Response({"detail": _(msg)}, status=404)

    def update(self, request, event_id, user_id):
        """ Updates fields passed in request """
        try:
            registration = Registration.objects.get(
                event__pk=event_id, user__user_id=user_id
            )
            self.check_object_permissions(self.request, registration)
            serializer = RegistrationSerializer(
                registration, data=request.data, partial=True, many=False
            )
            if serializer.is_valid():
                if registration.has_attended and request.data["has_attended"]:
                    return Response({"detail": _("User already attended")}, status=400)
                self.perform_update(serializer)
                if not request.data.get("has_attended"):
                    send_registration_mail(
                        request.data.get("is_on_wait"),
                        Event.objects.get(pk=event_id).title,
                        [User.objects.get(user_id=user_id).email],
                    )
                return Response(
                    {"detail": _("Registration successfully updated.")}, status=201
                )
            else:
                return Response({"detail": _("Could not perform update")}, status=400)
        except Registration.DoesNotExist:
            return Response({"detail": _("Could not find registration")}, status=404)
        except User.DoesNotExist:
            return Response({"detail": _("Could not find user")}, status=404)
        except Event.DoesNotExist:
            return Response({"detail": _("Could not find event")}, status=404)

        except ValidationError as e:
            return Response({"detail": _(e.message)}, status=404)

    def destroy(self, request, event_id, user_id):
        """ Unregisters the user specified with provided event_id and user_id """
        try:
            registration = Registration.objects.get(
                event__pk=event_id, user__user_id=user_id
            )
            event = Event.objects.get(pk=event_id)
            if event.sign_off_deadline < today():
                return Response(
                    {"detail": "Sign off deadline cannot be after deadline."},
                    status=400,
                )

            if request.id == user_id:
                return Response({"detail": registration.delete()}, status=200)

            self.check_object_permissions(request, registration)

            if is_admin_user(request):
                msg, status = registration.delete(), 200
            else:
                msg, status = _("You can only unregister yourself"), 403

        except Registration.DoesNotExist:
            msg, status = _("Could not delete registration."), 404
        except Event.DoesNotExist:
            msg = _("The provided event does not exist")

        return Response({"detail": msg}, status=status)
