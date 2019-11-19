from rest_framework import permissions
from django.db.models import Q

from app.content.models import User

import requests

from rest_framework.authtoken.models import Token


class IsMember(permissions.BasePermission):
	""" Checks if the user is a member """
	message = 'You are not a member'

	def has_permission(self, request, view):
		# Check if session-token is provided
		user_id = get_user_id(request)

		if user_id is None:
			return False

		return True


class IsAccessingItself(permissions.BasePermission):
	""" Checks if user is accessing themselves """
	message = 'You are not trying to access yourself'

	def has_permission(self, request, view):
		# Allow GET, CREATE, HEAD or OPTIONS requests
		if request.method in ['GET', 'CREATE', 'HEAD', 'OPTIONS']:
			return True
		elif request.method == 'PUT':
			return False

		# Check if session-token is provided
		user_id = get_user_id(request)

		if user_id is None:
			return False

		# Check for other user in url
		try:
			other_user = view.kwargs['user_id']
		except KeyError:
			other_user = None

		return user_id == other_user


class IsDev(permissions.BasePermission):
	""" Checks if the user is in HS or Drift """
	message = 'You are not in DevKom'

	def has_permission(self, request, view):
		return check_group_permission(self, request, view, ['DevKom'])


class IsHS(permissions.BasePermission):
	""" Checks if the user is in HS or Drift """
	message = 'You are not in HS'

	def has_permission(self, request, view):
		return check_group_permission(self, request, view, ['HS', 'DevKom'])


class IsPromo(permissions.BasePermission):
	""" Checks if the user is in HS, Drift, or Promo """
	message = 'You are not in Promo'

	def has_permission(self, request, view):
		return check_group_permission(self, request, view, ['HS', 'DevKom' 'Promo'])


class IsNoK(permissions.BasePermission):
	""" Checks if the user is in HS, Drift, or NoK """
	message = 'You are not in NoK'

	def has_permission(self, request, view):
		return check_group_permission(self, request, view, ['HS', 'DevKom', 'NoK'])


class IsNoKorPromo(permissions.BasePermission):
	""" Checks if the user is in HS, Drift, or NoK """
	message = 'You are not in NoK'

	def has_permission(self, request, view):
		return check_group_permission(self, request, view, ['HS', 'DevKom', 'NoK', 'Promo'])


def check_group_permission(self, request, view, groups):
	# Allow GET, HEAD or OPTIONS requests
	if request.method in permissions.SAFE_METHODS:
		return True

	# Check if session-token is provided
	user_id = get_user_id(request)

	if user_id is None:
		return False

	# Check if user with given id is connected to Groups
	return User.objects.filter(user_id=user_id).filter(groups__name__in=groups).count() > 0


def get_user_id(request):
	token = request.META.get('HTTP_X_CSRF_TOKEN')
	if token is None:
		return None

	try:
		userToken = Token.objects.get(key=token)
	except Token.DoesNotExist:
		return None
	request.id = userToken.user_id

	return userToken.user_id


def check_is_admin(request):
	""" Checks if user is in dev or HS """
	user_id = get_user_id(request)
	if user_id is None:
		return False
	return User.objects.filter(user_id=user_id).filter(groups__name__in=['DevKom', 'HS']).count() > 0

