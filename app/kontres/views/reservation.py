from django.db.models import Q
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.kontres.enums import ReservationStateEnum
from app.kontres.models.reservation import Reservation
from app.kontres.serializer.reservation_seralizer import ReservationSerializer


class ReservationViewSet(BaseViewSet):
    permission_classes = [BasicViewPermission]
    serializer_class = ReservationSerializer

    def get_queryset(self):
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        user_id = self.request.query_params.get("user_id")
        queryset = Reservation.objects.all()

        if start_date:
            start_date = parse_datetime(start_date)
        if end_date:
            end_date = parse_datetime(end_date)

        if start_date and end_date:
            queryset = Reservation.objects.filter(
                Q(start_time__lt=end_date) & Q(end_time__gt=start_date)
            )
            return queryset

        if user_id:
            if self.request.user.is_HS_or_Index_member:
                queryset = queryset.filter(author__user_id=user_id)
            else:
                raise PermissionDenied(
                    "Du har ikke tilgang til å se andres reservasjoner."
                )

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = ReservationSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.validated_data["author"] = request.user
            serializer.validated_data["state"] = ReservationStateEnum.PENDING
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        serializer = self.get_serializer(reservation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            previous_state = reservation.state
            new_state = serializer.validated_data.get("state")

            # Check if the state is being updated to CONFIRMED and set approved_by
            if (
                new_state == ReservationStateEnum.CONFIRMED
                and previous_state != ReservationStateEnum.CONFIRMED
            ):
                serializer.save(approved_by=request.user)
            else:
                serializer.save()

            if new_state and new_state != previous_state:
                if new_state == ReservationStateEnum.CONFIRMED:
                    serializer.instance.notify_approved()
                elif new_state == ReservationStateEnum.CANCELLED:
                    serializer.instance.notify_denied()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        super().destroy(self, request, *args, **kwargs)
        return Response(
            {"detail": "Reservasjonen ble slettet."}, status=status.HTTP_204_NO_CONTENT
        )
