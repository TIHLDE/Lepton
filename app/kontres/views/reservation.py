from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
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

        if start_date == "0" and end_date == "0":
            return Reservation.objects.all()
        elif start_date and end_date:
            return Reservation.objects.filter(
                start_time__gte=start_date, end_time__lte=end_date
            )
        else:
            return Reservation.objects.all()

    def retrieve(self, request, *args, **kwargs):
        reservation = self.get_object()
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.exists():
            serializer = ReservationSerializer(queryset, many=True)
            return Response({"reservations": serializer.data})
        else:
            return Response({"message": "No reservations found."})

    def create(self, request, *args, **kwargs):
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            # Overriding the state to PENDING
            serializer.validated_data["state"] = "PENDING"
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        reservation = self.get_object()

        print(request.user.groups)
        # Check if 'state' is in the request and if it has been changed.
        state_changed = (
            "state" in request.data and request.data["state"] != reservation.state
        )
        if state_changed:
            # If the user is not an HS or Index member, raise PermissionDenied.
            if not request.user.is_HS_or_Index_member:
                raise PermissionDenied(
                    "Du har ikke tilgang til å endre reservasjonsstatus"
                )
            # Additionally, check if the new state is valid.
            if request.data["state"] not in dict(ReservationStateEnum.choices).keys():
                raise ValidationError("Ugyldig tilstand for reservasjon.")

        serializer = self.get_serializer(reservation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            reservation = self.get_object()
            reservation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"Error occurred during deletion: {e}")
            raise

    def get_object(self):
        return get_object_or_404(Reservation, pk=self.kwargs.get("pk"))
