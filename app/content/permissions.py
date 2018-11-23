from rest_framework import permissions
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


