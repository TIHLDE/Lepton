from rest_framework import permissions
from django.db.models import Q

from app.content.models import User

import requests

# URL to the web-auth api
API_URL = 'https://web-auth.tihlde.org/api/v1'
VERIFY_URL = API_URL + '/verify'


class IsMember(permissions.BasePermission):
	""" Checks if the user is a member """
	message = 'You are not a member'

	def has_permission(self, request, view):
		# Check if session-token is provided
		user = get_user_info(request)

		if user is None:
			return False

		request.info = user
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
		user = get_user_info(request)

		if user is None:
			return False

		request.info = user

		# Check for other user in url
		try:
			other_user = view.kwargs['user_id']
		except KeyError:
			other_user = None

		return request.info['uid'][0] == other_user


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
	user = get_user_info(request)

	if user is None:
		return False

	request.info = user
	user_id = user['uid'][0]

	# Check if user with given id is connected to Groups
	return User.objects.filter(user_id=user_id).filter(groups__name__in=groups).count() > 0


def get_user_info(request):
	token = request.META.get('HTTP_X_CSRF_TOKEN')
	if token is None:
		return None
	# Get user ID from token
	headers = {'X-CSRF-TOKEN': token}
	r = requests.get(VERIFY_URL, headers=headers, verify=False)  # Send request to verify token
	response = r.json()

	if r.status_code is not 200 or 'uid' not in response:
		return None

	return response


def check_is_admin(request):
	""" Checks if user is in dev or HS """
	user = get_user_info(request)
	if user is None:
		return False
	user_id = user['uid'][0]
	return User.objects.filter(user_id=user_id).filter(groups__name__in=['DevKom', 'HS']).count() > 0

