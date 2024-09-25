from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.badge.models import Badge, UserBadge
from app.badge.serializers import BadgeSerializer, UserBadgeSerializer
from app.common.enums import Groups
from app.common.enums import NativeGroupType as GroupType
from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import (
    BasicViewPermission,
    IsDev,
    IsHS,
    is_admin_user,
)
from app.common.viewsets import BaseViewSet
from app.communication.enums import UserNotificationSettingType
from app.communication.notifier import Notify
from app.content.filters import UserFilter
from app.content.models import User
from app.content.models.event import Event
from app.content.serializers import (
    DefaultUserSerializer,
    EventListSerializer,
    UserCreateSerializer,
    UserListSerializer,
    UserMemberSerializer,
    UserPermissionsSerializer,
    UserSerializer,
)
from app.content.serializers.strike import UserInfoStrikeSerializer
from app.forms.serializers import FormPolymorphicSerializer
from app.group.models import Group, Membership
from app.group.serializers.membership import (
    MembershipHistorySerializer,
    MembershipSerializer,
)
from app.kontres.models.reservation import Reservation
from app.kontres.serializer.reservation_seralizer import ReservationSerializer
from app.util.export_user_data import export_user_data
from app.util.utils import CaseInsensitiveBooleanQueryParam


class UserViewSet(BaseViewSet, ActionMixin):
    """API endpoint to display one user"""

    serializer_class = UserSerializer
    permission_classes = [BasicViewPermission]
    queryset = User.objects.all()
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserFilter
    search_fields = ["user_id", "first_name", "last_name", "email"]

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            if is_admin_user(self.request):
                return UserListSerializer
            return DefaultUserSerializer
        return super().get_serializer_class()

    def retrieve(self, request, pk, *args, **kwargs):
        try:
            user = self._get_user(request, pk)

            self.check_object_permissions(self.request, user)

            serializer = DefaultUserSerializer(user)

            if is_admin_user(self.request) or user == request.user:
                serializer = UserSerializer(user, context={"request": self.request})

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"message": "Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=self.request.data)

        if serializer.is_valid():
            user = super().perform_create(serializer)
            return Response(
                {"detail": DefaultUserSerializer(user).data},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, pk, *args, **kwargs):
        """Updates fields passed in request"""
        user = self._get_user(request, pk)
        self.check_object_permissions(self.request, user)
        if is_admin_user(request):
            serializer = UserSerializer(
                user,
                context={"request": request},
                data=request.data,
            )
        else:
            if self.request.id == pk:
                serializer = UserMemberSerializer(
                    user,
                    context={"request": request},
                    data=request.data,
                )
            else:
                return Response(
                    {"detail": "Du har ikke tillatelse til å oppdatere brukeren"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        if serializer.is_valid():
            super().perform_update(serializer)
            user = get_object_or_404(User, user_id=pk)
            serializer = UserSerializer(
                user,
                context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "Kunne ikke oppdatere brukeren"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk, *args, **kwargs):
        user = self._get_user(request, pk)
        self.check_object_permissions(self.request, user)
        self.perform_destroy(user)
        return Response(
            {"detail": "Brukeren har bltt slettet"},
            status=status.HTTP_200_OK,
        )

    def _get_user(self, request, pk):
        if pk == "me":
            return request.user
        return get_object_or_404(User, user_id=pk)

    @action(detail=False, methods=["post"], url_path="me/slack")
    def connect_to_slack(self, request, *args, **kwargs):
        user = self.request.user
        self.check_object_permissions(self.request, user)

        code = request.data.get("code", None)

        if not code:
            return Response(
                {"detail": 'Du må sende med "code" fra Slack-autentisering'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from app.communication.slack import get_slack_user_id

        user.slack_user_id = get_slack_user_id(code)
        user.save(update_fields=["slack_user_id"])

        return Response(
            {"detail": "Vi har koblet brukeren din på TIHLDE.org til din Slack-bruker"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="me/permissions")
    def get_user_permissions(self, request, *args, **kwargs):
        try:
            serializer = UserPermissionsSerializer(
                request.user, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Kunne ikke hente brukerens tillatelser"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"], url_path="memberships")
    def get_user_memberships(self, request, pk, *args, **kwargs):
        user = self._get_user(request, pk)
        self.check_object_permissions(self.request, user)

        memberships = user.memberships.filter(
            group__type__in=GroupType.public_groups()
        ).order_by("-created_at")
        return self.paginate_response(
            data=memberships,
            serializer=MembershipSerializer,
            context={"request": request},
        )

    @action(detail=True, methods=["get"], url_path="memberships-with-fines")
    def get_user_memberships_with_fines(self, request, pk, *args, **kwargs):
        user = self._get_user(request, pk)
        self.check_object_permissions(self.request, user)

        memberships = user.memberships.filter(
            group__type__in=GroupType.public_groups(), group__fines_activated=True
        ).order_by("-created_at")
        return self.paginate_response(
            data=memberships,
            serializer=MembershipSerializer,
            context={"request": request},
        )

    @action(detail=True, methods=["get"], url_path="membership-histories")
    def get_user_membership_histories(self, request, pk, *args, **kwargs):
        user = self._get_user(request, pk)
        self.check_object_permissions(self.request, user)

        memberships = user.membership_histories.filter(
            group__type__in=GroupType.public_groups()
        )
        return self.paginate_response(
            data=memberships,
            serializer=MembershipHistorySerializer,
            context={"request": request},
        )

    def post_user_badges(self, request, *args, **kwargs):
        import uuid

        user = self.request.user
        try:
            flag = uuid.UUID(request.data.get("flag"))
        except ValueError:
            return Response(
                {"detail": "Ugyldig flagg"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        badge = get_object_or_404(Badge, flag=flag)

        if not badge.is_active:
            return Response(
                {"detail": "Badgen er ikke aktiv"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_badge = UserBadge(user=user, badge=badge)
        serializer = UserBadgeSerializer(
            user_badge, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            try:
                super().perform_create(serializer)
                return Response(
                    {"detail": "Badge fullført!"}, status=status.HTTP_200_OK
                )
            except IntegrityError:
                return Response(
                    {"detail": "Du har allerede mottatt denne badgen"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "Badgen kunne ikke bli opprettet"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_user_detail_badges(self, request, *args, **kwargs):
        user = self._get_user(request, kwargs["pk"])
        user_badges = user.user_badges.order_by("-created_at")
        badges = [
            user_badge.badge
            for user_badge in user_badges
            if user_badge.badge.is_public
            or request.user.user_badges.filter(badge=user_badge.badge).exists()
        ]

        return self.paginate_response(data=badges, serializer=BadgeSerializer)

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="badges",
    )
    def get_or_post_detail_user_badges(self, request, *args, **kwargs):
        if request.method == "GET":
            return self.get_user_detail_badges(request, *args, **kwargs)
        elif request.method == "POST":
            return self.post_user_badges(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="me/strikes")
    def get_user_strikes(self, request, *args, **kwargs):
        strikes = request.user.strikes.active()
        serializer = UserInfoStrikeSerializer(
            instance=strikes, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="strikes")
    def get_user_detail_strikes(self, request, *args, **kwargs):
        user = self.get_object()
        strikes = user.strikes.active()
        serializer = UserInfoStrikeSerializer(
            instance=strikes, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="me/events")
    def get_user_events(self, request, *args, **kwargs):
        filter_field = self.request.query_params.get("expired")
        event_has_ended = CaseInsensitiveBooleanQueryParam(filter_field).value

        now = timezone.now()

        if event_has_ended:
            events = Event.objects.filter(
                registered_users_list=request.user, end_date__lte=now
            ).order_by("-start_date")
        else:
            events = Event.objects.filter(
                registered_users_list=request.user, end_date__gt=now
            ).order_by("start_date")

        return self.paginate_response(
            data=events, serializer=EventListSerializer, context={"request": request}
        )

    @action(detail=False, methods=["get"], url_path="me/forms")
    def get_user_forms(self, request, *args, **kwargs):
        forms = request.user.forms

        filter_field = request.query_params.get("unanswered")
        filter_unanswered = CaseInsensitiveBooleanQueryParam(filter_field)

        if filter_unanswered:
            forms = request.user.get_unanswered_evaluations()

        return self.paginate_response(
            data=forms,
            serializer=FormPolymorphicSerializer,
            context={"request": request},
        )

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
        Notify(
            [user], "Brukeren din er godkjent", UserNotificationSettingType.OTHER
        ).add_paragraph(f"Hei, {user.first_name}!").add_paragraph(
            "Vi har godkjent brukeren din på TIHLDE.org! Du kan nå logge inn og ta i bruk siden."
        ).add_link(
            "Logg inn", "/logg-inn/"
        ).send()
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
        Notify(
            [user], "Brukeren din ble ikke godkjent", UserNotificationSettingType.OTHER
        ).add_paragraph(f"Hei, {user.first_name}!").add_paragraph(
            "Vi har avslått brukeren din på TIHLDE.org fordi den ikke oppfylte kravene til å ha bruker. Du kan lage en ny bruker der du har rettet feilen hvis du ønsker. Kontakt oss hvis du er uenig i avgjørelsen."
        ).add_paragraph(
            f"Vedlagt begrunnelse: {reason}."
        ).add_link(
            "Til forsiden", "/"
        ).send()
        user.delete()
        return Response(
            {"detail": "Brukeren ble avslått og har blitt informert på epost"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="me/data")
    def export_user_data(self, request, *args, **kwargs):
        export_successfull = export_user_data(request, request.user)

        if export_successfull:
            return Response(
                {
                    "detail": "Vi har sendt en epost til din registrerte epost-adresse med dine data vedlagt"
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Noe gikk galt, prøv igjen senere eller kontakt Index"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @action(detail=False, methods=["get"], url_path="me/reservations")
    def get_user_reservations(self, request, *args, **kwargs):
        user = request.user
        reservations = Reservation.objects.filter(author=user).order_by("start_time")
        serializer = ReservationSerializer(
            reservations, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
