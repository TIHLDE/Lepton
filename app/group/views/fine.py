from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.content.models.user import User
from app.content.serializers.user import UserFineSerializer
from app.group.filters.fine import FineFilter
from app.group.mixins import APIFineErrorsMixin
from app.group.models.fine import Fine
from app.group.serializers.fine import FineCreateSerializer, FineSerializer
from rest_framework.decorators import action

from app.util.utils import get_apposing_filters_params



class FineViewSet(viewsets.ModelViewSet, APIFineErrorsMixin):
    serializer_class = FineSerializer
    permission_classes = [BasicViewPermission]
    queryset = Fine.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = FineFilter
    pagination_class = BasePagination

    def get_queryset(self):
        return self.queryset.filter(
            group__slug=self.kwargs["slug"], group__fines_activated=True
        )

    def create(self, request, *args, **kwargs):
        context = {
            "group_slug": kwargs["slug"],
            "created_by": request.id,
            "user_ids": request.data["user"],
            "request": request,
        }

        serializer = FineCreateSerializer(
            many=True, partial=True, data=[request.data], context=context
        )

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": ("Boten ble slettet")}, status=status.HTTP_200_OK)

    
    
    def get_fine_filters(self, request):
        
        return {
            **get_apposing_filters_params(request, "payed", "not_payed", "payed"),
            **get_apposing_filters_params(request, "approved", "not_approved", "approved")

        }



        
    @action(detail=False, methods=["get"], url_path="users")
    def get_fine_users (self, request, *args, **kwargs):
        filters =  self.get_fine_filters(request)
        users = User.objects.filter(memberships__group__slug = self.kwargs["slug"])
        if filters.get("payed", None):
            users.exclude(fines__payed=False)
        print(users)
        if filters.get("approved", None):
            users.filter(fines__payed=filters["approved"])
        return Response( UserFineSerializer(users, many = True, context = {"filters": filters, "slug":self.kwargs["slug"]}).data, status=status.HTTP_200_OK)
        
        
        
        
    
    
    
