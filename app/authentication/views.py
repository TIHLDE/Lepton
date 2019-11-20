from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes

from ..content.permissions.permissions import IsDev, IsHS

from .serializers import AuthSerializer, MakeSerializer

from ..content.models.user import User
from rest_framework.authtoken.models import Token


@api_view(['POST'])
def login(request):
	# Serialize data and check if valid
	serializer = AuthSerializer(data=request.data)
	if(not serializer.is_valid()):
		return Response({'detail': ('Invalid user_id or password')}, status=400)

	# Get username and password
	user_id = serializer.data['user_id']
	password = serializer.data['password']

	user = User.objects.get(user_id = user_id)
	if user.check_password(password):
		try:
			token = Token.objects.get(user_id=user_id).key
			return Response({'token': token}, status=400)
		except Token.DoesNotExist:
			return Response({'detail': ('Not a TIHLDE member')}, status=400)
	else:
		return Response({'detail': ('Incorrect user_id or password')}, status=400)

@api_view(['POST'])
@permission_classes([IsDev, IsHS])
def makeMember(request):
	# Serialize data and check if valid
	serializer = MakeSerializer(data=request.data)
	if(not serializer.is_valid()):
  		return Response({'detail': ('Invalid user_id')}, status=400)

	# Get username and password
	user_id = serializer.data['user_id']

	user = User.objects.get(user_id = user_id)
	if user is not None:
		try:
			token = Token.objects.get(user_id=user_id)
			return Response({'detail': ('Already a TIHLDE member')}, status=500)
		except Token.DoesNotExist:
			Token.objects.create(user=user)
			return Response({'detail': ('New TIHLDE member added')}, status=500)
	else:
		return Response({'detail': ('Incorrect user_id')}, status=500)