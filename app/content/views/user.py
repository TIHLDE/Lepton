from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.enums import Groups, GroupType
from app.common.pagination import BasePagination
from app.common.permissions import (
    BasicViewPermission,
    IsDev,
    IsHS,
    is_admin_user,
)
from app.content.filters import UserFilter
from app.content.models import User
from app.content.serializers import (
    BadgeSerializer,
    EventListSerializer,
    StrikeSerializer,
    UserAdminSerializer,
    UserCreateSerializer,
    UserListSerializer,
    UserMemberSerializer,
    UserSerializer,
)
from app.group.models import Group, Membership
from app.group.serializers import DefaultGroupSerializer
from app.util.mail_creator import MailCreator
from app.util.notifier import Notify


class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint to display one user """

    serializer_class = UserSerializer
    permission_classes = [BasicViewPermission]
    queryset = User.objects.all()
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserFilter
    search_fields = ["user_id", "first_name", "last_name"]

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            return UserListSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        try:
            user = request.user
            self.check_object_permissions(self.request, user)
            serializer = UserSerializer(
                user, context={"request": self.request}, many=False
            )

            return Response(serializer.data)
        except User.DoesNotExist as user_not_exist:
            capture_exception(user_not_exist)
            return Response(
                {"detail": ("Kunne ikke finne brukeren")},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=self.request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": serializer.data}, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, pk, *args, **kwargs):
        """ Updates fields passed in request """
        try:
            user = get_object_or_404(User, user_id=pk)
            self.check_object_permissions(self.request, user)
            if is_admin_user(request):
                serializer = UserAdminSerializer(
                    user, context={"request": request}, many=False, data=request.data,
                )
            else:
                if self.request.id == pk:
                    serializer = UserMemberSerializer(
                        user,
                        context={"request": request},
                        many=False,
                        data=request.data,
                    )
                else:
                    return Response(
                        {"detail": ("Du har ikke tillatelse til å oppdatere brukeren")},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            if serializer.is_valid():
                serializer.save()
                serializer = UserMemberSerializer(
                    User.objects.get(user_id=pk),
                    context={"request": request},
                    many=False,
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": ("Kunne ikke oppdatere brukeren")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ObjectDoesNotExist as object_not_exist:
            capture_exception(object_not_exist)
            return Response(
                {"detail": "Kunne ikke finne brukeren"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["get"], url_path="me/group")
    def get_user_memberships(self, request, *args, **kwargs):
        memberships = request.user.memberships.all()
        groups = [
            membership.group
            for membership in memberships
            if membership.group.type in GroupType.public_groups()
        ]
        serializer = DefaultGroupSerializer(
            groups, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="me/badge")
    def get_user_badges(self, request, *args, **kwargs):
        user_badges = request.user.user_badges.order_by("-created_at")
        badges = [user_badge.badge for user_badge in user_badges]
        page = self.paginate_queryset(badges)
        serializer = BadgeSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["get"], url_path="me/strikes")
    def get_user_strikes(self, request, *args, **kwargs):
        strikes = request.user.strikes.all()
        active_strikes = [strike for strike in strikes if strike.active]
        page = self.paginate_queryset(active_strikes)
        serializer = StrikeSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["get"], url_path="me/events")
    def get_user_events(self, request, *args, **kwargs):
        registrations = request.user.registrations.all()
        events = [
            registration.event
            for registration in registrations
            if not registration.event.expired
        ]
        page = self.paginate_queryset(events)
        serializer = EventListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="activate",
        permission_classes=(IsHS | IsDev,),
    )
    def makeTIHLDEMember(self, request, *args, **kwargs):
        TIHLDE = Group.objects.get(slug=Groups.TIHLDE)
        user_id = request.data["user_id"]
        user = get_object_or_404(User, user_id=user_id)
        Membership.objects.get_or_create(user=user, group=TIHLDE)
        Notify(user, "Brukeren din er godkjent").send_email(
            MailCreator("Brukeren din er godkjent")
            .add_paragraph(f"Hei {user.first_name}!")
            .add_paragraph(
                "Vi har godkjent brukeren din på TIHLDE.org! Du kan nå logge inn og ta i bruk siden."
            )
            .add_button("Logg inn", "https://tihlde.org/logg-inn/")
            .generate_string()
        )
        return Response(
            {
                "detail": "Brukeren ble lagt til som TIHLDE-medlem og har blitt informert på epost"
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="decline",
        permission_classes=(IsHS | IsDev,),
    )
    def declineTIHLDEMember(self, request, *args, **kwargs):
        user_id = request.data["user_id"]
        try:
            reason = request.data["reason"]
            if reason is None or len(reason) == 0:
                reason = "Begrunnelse er ikke oppgitt"
        except KeyError:
            reason = "Begrunnelse er ikke oppgitt"
        user = get_object_or_404(User, user_id=user_id)
        Notify(user, "Brukeren din ble ikke godkjent").send_email(
            MailCreator("Brukeren din ble ikke godkjent")
            .add_paragraph(f"Hei {user.first_name}!")
            .add_paragraph(
                "Vi har avslått brukeren din på TIHLDE.org fordi den ikke oppfylte kravene til å ha bruker. Du kan lage en ny bruker der du har rettet feilen hvis du ønsker. Kontakt oss hvis du er uenig i avgjørelsen."
            )
            .add_paragraph(f"Vedlagt begrunnelse: {reason}.")
            .add_button("Til forsiden", "https://tihlde.org/")
            .generate_string()
        )
        user.delete()
        return Response(
            {"detail": "Brukeren ble avslått og har blitt informert på epost"},
            status=status.HTTP_200_OK,
        )
