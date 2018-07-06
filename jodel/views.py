from django.shortcuts import render

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render
from .models import Jodel
from .serializers import JodelSerializer

class JodelViewSet(viewsets.ModelViewSet):
    queryset = Jodel.objects.all()
    serializer_class = JodelSerializer

    @action(['GET'], detail=False)
    def top(request, format=None):
        """
        Lists the jodels ordered by votes DESC
        """
        jodels = Jodel.objects.order_by('-votes')
        serializer = JodelSerializer(jodels, many=True)
        return Response(serializer.data)

    @action(['GET', 'PATCH'], detail=True)
    def upvote(self, request, pk=None):
        """
        Upvotes a jodel and responds with the new Jodel.
        """
        jodel = self.get_object()
        jodel.votes = jodel.votes + 1
        jodel.save()
        serializer = JodelSerializer(jodel)
        return Response(serializer.data)

    @action(['GET', 'PATCH'], detail=True)
    def downvote(self, request, pk=None):
        """
        Downvotes a jodel and responds with the new Jodel.
        """
        jodel = self.get_object()
        jodel.votes = jodel.votes - 1
        jodel.save()
        serializer = JodelSerializer(jodel)
        return Response(serializer.data)
