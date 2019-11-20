from rest_framework import routers
from django.conf.urls import url
from django.urls import path
from django.conf.urls import include

from .views import (login, makeMember)

from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()

# Register content viewpoints here
urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^login', login),
    url(r'^make', makeMember),
    # url(r'^token', obtain_auth_token), #Used to bypass all restrictions when getting token

]
