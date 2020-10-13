from rest_framework import viewsets
from rest_framework.response import Response

from ..models import WikiPost
from ..permissions import IsDev, IsHS
from ..serializers import WikiListSerializer, WikiPostSerializer


class WikiViewSet(viewsets.ModelViewSet):
    queryset = WikiPost.objects.all()
    serializer_class = WikiPostSerializer
    permission_classes = [IsHS | IsDev]
    lookup_field = "slug"

    def list(self, request):
        serializer = WikiListSerializer(self.queryset, many=True)
        return Response(serializer.data)
