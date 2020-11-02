from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import UserPermission, is_admin_user
from app.content.models import User
from app.content.serializers import (
    UserAdminSerializer,
    UserCreateSerializer,
    UserMemberSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint to display one user """

    serializer_class = UserSerializer
    permission_classes = [UserPermission]
    queryset = User.objects.all()
    pagination_class = BasePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["user_class", "user_study", "is_TIHLDE_member"]
    search_fields = ["user_id", "first_name", "last_name"]

    def retrieve(self, request, *args, **kwargs):
        try:
            user = request.user
            self.check_object_permissions(self.request, user)
            serializer = UserSerializer(
                user, context={"request": self.request}, many=False
            )

            return Response(serializer.data)
        except User.DoesNotExist:
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
            self.check_object_permissions(self.request, User.objects.get(user_id=pk))
            if is_admin_user(request):
                if self.request.id == pk:
                    serializer = UserMemberSerializer(
                        User.objects.get(user_id=pk),
                        context={"request": request},
                        many=False,
                        data=request.data,
                    )
                else:
                    serializer = UserAdminSerializer(
                        User.objects.get(user_id=pk),
                        context={"request": request},
                        many=False,
                        data=request.data,
                    )
            else:
                if self.request.id == pk:
                    serializer = UserMemberSerializer(
                        User.objects.get(user_id=pk),
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
                return Response({"detail": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": ("Kunne ikke oppdatere brukeren")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ObjectDoesNotExist:
            return Response(
                {"detail": "Kunne ikke finne brukeren"},
                status=status.HTTP_404_NOT_FOUND,
            )
