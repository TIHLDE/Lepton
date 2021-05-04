from django.conf.urls import include, url
from rest_framework import routers

from app.authentication.views import login

router = routers.DefaultRouter()

# Register content viewpoints here
urlpatterns = [
    url(r"", include(router.urls)),
    url(r"^login", login),
    url(r"^rest-auth/", include("rest_auth.urls")),
    url(r"^", include("django.contrib.auth.urls")),
    # url(r'^token', obtain_auth_token), #Used to bypass all restrictions when getting token
]
