from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.permissions import IsDev, IsHS
from app.content.models import WikiPost
from app.content.serializers import WikiListSerializer, WikiPostSerializer


class WikiViewSet(viewsets.ModelViewSet):
    queryset = WikiPost.objects.all()
    serializer_class = WikiPostSerializer
    permission_classes = [IsHS | IsDev]
    lookup_field = "slug"

    def list(self, request):
        serializer = WikiListSerializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
