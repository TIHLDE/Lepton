from django.conf.urls import include
from django.conf.urls import url
from rest_framework import routers

from .views import (login, makeMember)

router = routers.DefaultRouter()

# Register content viewpoints here
urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^login', login),
    url(r'^make', makeMember),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^', include('django.contrib.auth.urls')),
    # url(r'^token', obtain_auth_token), #Used to bypass all restrictions when getting token

]
