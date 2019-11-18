from rest_framework import routers
from django.conf.urls import url
from django.urls import path
from django.conf.urls import include

from .views import (login, logout, verify)

router = routers.DefaultRouter()

# Register content viewpoints here
urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^token', login),
    url(r'^logout', logout),
    url(r'^verify', verify)
]
