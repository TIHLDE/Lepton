from rest_framework import permissions
from django.db.models import Q

from .models import Connection

import requests

# URL to the web-auth api
API_URL = 'https://web-auth.tihlde.org/api/v1'
VERIFY_URL = API_URL + '/verify'

# Checks if the user is a member
class IsMemberOrSafe(permissions.BasePermission):
    message = 'You are not a member'

    def has_permission(self, request, view):
        # Allow GET, HEAD or OPTIONS requests
        if(request.method in permissions.SAFE_METHODS):
            return True

        # Check if session-token is provided
        token = request.META.get('HTTP_X_CSRF_TOKEN')
        if(token == None):
            return permissions.IsAdminUser.has_permission(self, request, view) # Allow access if is Admin

        # Verify user
        headers = {'X-CSRF-TOKEN': token}
        authReq = requests.get(VERIFY_URL, headers=headers, verify=False)
        status_code = authReq.status_code
        return status_code == 200


# Checks if the user is in HS or Drift
class IsHSorDrift(permissions.BasePermission):
    message = 'You are not in HS or Drift'

    def has_permission(self, request, view):
        return check_group_permission(self, request, view, ['HS', 'Drift'])


# Checks if the user is in HS, Drift, or Promo
class HS_Drift_Promo(permissions.BasePermission):
    message = 'You are not in HS, Drift or Promo'

    def has_permission(self, request, view):
        return check_group_permission(self, request, view, ['HS', 'Drift', 'Promo'])


# Checks if the user is in HS, Drift, or NoK
class HS_Drift_NoK(permissions.BasePermission):
    message = 'You are not in HS, Drift or NoK'

    def has_permission(self, request, view):
        return check_group_permission(self, request, view, ['HS', 'Drift', 'NoK'])
        

def check_group_permission(self, request, view, groups):
    # Allow GET, HEAD or OPTIONS requests
    if(request.method in permissions.SAFE_METHODS):
        return True

    # Check if session-token is provided
    token = request.META.get('HTTP_X_CSRF_TOKEN')
    if(token == None):
        return permissions.IsAdminUser.has_permission(self, request, view) # Allow access if is Admin

    # Gets the user id
    user = get_user_id(token)

    if(user is None): return False

    # Check if user with given id is connected to Drift or Hovedstyret
    return Connection.objects.filter(user_id = user).filter(group__abbr__in=groups).count() > 0


def get_user_id(token):
    # Get user ID from token
    headers = {'X-CSRF-TOKEN': token}
    r = requests.get(VERIFY_URL, headers=headers, verify=False) # Send request to verify token
    response = r.json()

    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        response.method + ' ' + response.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        response.body,
    ))
    
    if(r.status_code is not 200 or 'uid' not in response):
        return None

    # User id
    user = response['uid'][0]

    return user



        