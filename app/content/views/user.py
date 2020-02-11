from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.response import Response

from ..models import User
from ..permissions import UserPermission
from ..serializers import UserSerializer, UserMemberSerializer, UserCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint to display one user """
    serializer_class = UserSerializer
    permission_classes = [UserPermission]
    queryset = User.objects.all()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_class', 'user_study']
    search_fields = ['user_id']

    def retrieve(self, request, *args, **kwargs):
        try:
            user = request.user
            self.check_object_permissions(self.request, user)
            serializer = UserSerializer(user, context={'request': self.request}, many=False)

            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'detail': _('User not found.')}, status=404)

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=self.request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': _('User created')}, status=201)

        return Response({'detail': serializer.errors}, status=400)

    def update(self, request, pk, *args, **kwargs):
        """ Updates fields passed in request """
        try:
            self.check_object_permissions(self.request, User.objects.get(user_id=pk))
            if self.request.id == pk:
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
