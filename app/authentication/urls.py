from django.urls import include, re_path
from rest_framework import routers

from app.authentication.views import login

router = routers.DefaultRouter()

# Register content viewpoints here
urlpatterns = [
    re_path(r"", include(router.urls)),
    re_path(r"^login", login),
    re_path(r"^rest-auth/", include("dj_rest_auth.urls")),
    re_path(r"^", include("django.contrib.auth.urls")),
    # re_path(r'^token', obtain_auth_token), #Used to bypass all restrictions when getting token
]
