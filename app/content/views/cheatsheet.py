from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..pagination import BasePagination

from ..filters import CheatsheetFilter
from ..permissions import is_admin_user, IsMember
from ..models import Cheatsheet
from ..serializers import CheatsheetSerializer
from app.content.enums import UserClass, UserStudy

class CheatsheetViewSet(viewsets.ModelViewSet):
    serializer_class = CheatsheetSerializer
    permission_classes = [IsMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    queryset = Cheatsheet.objects.all()
    pagination_class = BasePagination
    filterset_class = CheatsheetFilter
    search_fields = ['course', 'title', 'creator']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return CheatsheetFilter(self.request.GET, queryset=queryset).qs

    def list(self, request, study, grade):
        try:
            cheatsheet = self.filter_queryset(self.queryset).filter(grade=UserClass[grade], study=UserStudy[study])
            page = self.paginate_queryset(cheatsheet)
            if page is not None:
                serializer = CheatsheetSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = CheatsheetSerializer(
            cheatsheet, context={'request': request}, many=True)
            return Response(serializer.data, status=200)
        except Cheatsheet.DoesNotExist:
            return Response({'detail': _('Cheatsheets does not exist.')}, status=404)

    def create(self, request, *args, **kwargs):
        if is_admin_user(request):
            serializer = CheatsheetSerializer(data=self.request.data, many=False)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail': _('Cheatsheet created')}, status=201)
            return Response({'detail': serializer.errors}, status=400)
        return Response({'detail': _('Not authenticated to perform cheatsheet creation')}, status=400)
    
    def update(self, request, study, grade, pk):
        try:
            cheatsheet = self.queryset.get(
                id=pk, grade=UserClass[grade], study=UserStudy[study])
            if is_admin_user(request):
                serializer = CheatsheetSerializer(cheatsheet, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'detail': ('Cheatsheet successfully updated.')}, status=204)
            return Response({'detail': ('Not authenticated to perform cheatsheet update')}, status=400)
        except Cheatsheet.DoesNotExist:
            return Response({'details': _('Cheatsheet not found')}, status=404)
    
    def destroy(self, request, study, grade, pk):
        try:
            cheatsheet = self.queryset.get(
                id=pk, grade=UserClass[grade], study=UserStudy[study])
            if is_admin_user(request):
                return Response({'detail': (cheatsheet.delete())}, status=200)
            return Response({'detail': ('Not authenticated to perform cheatsheet deletion')}, status=204)
        except Cheatsheet.DoesNotExist:
            return Response({'details': _('Cheatsheet not found')}, status=404)