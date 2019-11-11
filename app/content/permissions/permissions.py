from rest_framework import permissions
from django.db.models import Q

from app.content.models import User

import requests

# URL to the web-auth api
API_URL = 'https://web-auth.tihlde.org/api/v1'
VERIFY_URL = API_URL + '/verify'


# Checks if the user is a member
class IsMember(permissions.BasePermission):
	message = 'You are not a member'

	def has_permission(self, request, view):
		# Check if session-token is provided
		user = get_user_info(request)

		if user is None:
			return False

		request.info = user
		return True

	def isDev(self, request):
		user = get_user_info(request)
		if user is None:
			return False
		user_id = user['uid'][0]
		return User.objects.filter(user_id=user_id).filter(groups__name__in= ['DevKom','HS']).count() > 0


# Checks if the user is in HS or Drift
class IsDev(permissions.BasePermission):
	message = 'You are not in DevKom'

	def has_permission(self, request, view):
		return check_group_permission(self, request, view, ['DevKom'])


# Checks if the user is in HS or Drift
class IsHS(permissions.BasePermission):
	message = 'You are not in HS'

	def has_permission(self, request, view):
		return check_group_permission(self, request, view, ['HS', 'DevKom'])


# Checks if the user is in HS, Drift, or Promo
class IsPromo(permissions.BasePermission):
	message = 'You are not in Promo'

	def has_permission(self, request, view):
		return check_group_permission(self, request, view, ['HS', 'DevKom' 'Promo'])


# Checks if the user is in HS, Drift, or NoK
class IsNoK(permissions.BasePermission):
	message = 'You are not in NoK'

	def has_permission(self, request, view):
		return check_group_permission(self, request, view, ['HS', 'DevKom', 'NoK'])


# Checks if the user is in HS, Drift, or NoK
class IsNoKorPromo(permissions.BasePermission):
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