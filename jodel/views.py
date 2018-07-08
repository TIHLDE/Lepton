from django.shortcuts import render

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from .models import Jodel, Comment
from .serializers import JodelSerializer, JodelWithCommentsSerializer, CommentSerializer

class JodelViewSet(viewsets.ModelViewSet):
    queryset = Jodel.objects.all()
    serializer_class = JodelSerializer

    def list(self, request):
        print('LISTING!')
        return super().list(request)


    @action(['GET'], detail=False)
    def top(request, format=None):
        """
        Lists the jodels ordered by votes DESC
        """
        jodels = Jodel.objects.order_by('-votes')
        serializer = JodelSerializer(jodels, many=True)
        return Response(serializer.data)

    @action(['GET', 'POST'], detail=True, url_path='comments')
    def comments(self, request, pk=True):
        """
        GET: Returns a list of all the comments for the current jodel.
        POST: Adds a comment to the current jodel and returns it.
        """
        print('COMMENTS!: ', request.method)
        if request.method == 'GET':
            jodel = self.get_object()
            comments = Comment.objects.filter(parent=jodel)
            serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data)

        elif request.method == 'POST':
            jodel = self.get_object()
            serializer = CommentSerializer(data=request.data, context={'request': request, 'parent_id': jodel.pk})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(['GET'], detail=True, url_path='all')
    def jodel_with_comments(self, request, **kwargs):
        """
        GET: Returns a jodel with all their comments.
        """
        if request.method == 'GET':
            jodel = self.get_object()
            serializer = JodelWithCommentsSerializer(jodel, many=False, context={'request': request})
            return Response(serializer.data)

    @action(['GET'], detail=False, url_path='all')
    def jodels_with_comments(self, request, **kwargs):
        """
        GET: Returns all jodels with all their comments.
        """
        if request.method == 'GET':
            jodels = Jodel.objects.all()
            serializer = JodelWithCommentsSerializer(jodels, many=True, context={'request': request})
            return Response(serializer.data)


    @action(['GET', 'DELETE', 'PATCH'], detail=True, url_path='comments/(?P<cpk>[a-z0-9]+)')
    def comments_details(self, request, **kwargs):
        """
        GET: Returns a list of all the comments for the current jodel.
        DELETE: Deletes the comment. Returns 204 (no content).
        PATCH: Updates the comment. Reeturns 200 with the updated comment.
        """
        cpk = self.kwargs['cpk']

        try:
            comment = Comment.objects.get(pk=cpk)

            if request.method == 'GET':
                # works
                serializer = CommentSerializer(comment, many=False, context={'request': request})
                return Response(serializer.data)

            elif request.method == 'DELETE':
                # works
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            elif request.method == 'PATCH':
                # works
                serializer = CommentSerializer(comment, data=request.data, partial=True, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(data=serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
