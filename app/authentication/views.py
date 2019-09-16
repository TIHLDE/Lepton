from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from rest_framework import status, viewsets
from rest_framework.decorators import api_view

from .serializers import AuthSerializer, GroupSerializer, ConnectionSerializer
from .models import Group, Connection
from .permissions import IsHSorDrift

# http-lib import
import requests

# URL to the web-auth api
API_URL = 'https://web-auth.tihlde.org/api/v1'
TOKEN_URL = API_URL + '/auth'
VERIFY_URL = API_URL + '/verify'
LOGOUT_URL = API_URL + '/logout'


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('-created_at')
    serializer_class = GroupSerializer
    permission_classes = [IsHSorDrift]

class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connection.objects.all().order_by('-created_at')
    serializer_class = ConnectionSerializer
    permission_classes = [IsHSorDrift]

@api_view(['POST'])
def login(request):
    
    # Serialize data and check if valid
    serializer = AuthSerializer(data=request.data)
    if(not serializer.is_valid()):
        return HttpResponse(content="Credentials not provided", status=status.HTTP_400_BAD_REQUEST)

    # Get username and password
    username = serializer.data['username']
    password = serializer.data['password']

    # Send token-request to web-auth API
    r = requests.post(TOKEN_URL, json={'username': username, 'password': password}, verify=False)
    response = r.json()
    
    # Send response back
    if(r.status_code == 200 or r.status_code == 401):
        return JsonResponse(data=response, status=r.status_code)
    else:
        return HttpResponse(status=500)

@api_view(['POST'])
def logout(request):

    # Check if session-token is provided
    token = request.META.get('HTTP_X_CSRF_TOKEN')
    if(token == None):
        return JsonResponse(data={'msg': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Logout user
    headers = {'X-CSRF-TOKEN': token}
    r = requests.post(LOGOUT_URL, headers=headers, verify=False)
    return HttpResponse(status=r.status_code)

@api_view(['GET'])
def verify(request):

    # Check if session-token is provided
    token = request.META.get('HTTP_X_CSRF_TOKEN')
    if(token == None):
        return JsonResponse(data={'msg': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Verify user
    headers = {'X-CSRF-TOKEN': token}
    r = requests.get(VERIFY_URL, headers=headers, verify=False)
    response = r.json()
    return JsonResponse(data=response, status=r.status_code)
