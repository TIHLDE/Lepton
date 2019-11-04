from rest_framework import permissions
from django.db.models import Q


import requests

# URL to the web-auth api
API_URL = 'https://web-auth.tihlde.org/api/v1'
VERIFY_URL = API_URL + '/verify'
