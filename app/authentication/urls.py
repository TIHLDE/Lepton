from django.urls import include, re_path
from rest_framework import routers

from app.authentication.views import (
    login,
    get_oauth_app,
    oauth_access_token,
    temporary_oauth_code,
)

router = routers.DefaultRouter()

# Register content viewpoints here
urlpatterns = [
    re_path(r"", include(router.urls)),
    re_path(r"^login", login),
    re_path(r"^oauth/access_token", oauth_access_token),
    re_path(r"^oauth/oauth_app", get_oauth_app),
    re_path(r"^oauth/redirect", temporary_oauth_code),
    re_path(r"^rest-auth/", include("dj_rest_auth.urls")),
    re_path(r"^", include("django.contrib.auth.urls")),
    # re_path(r'^token', obtain_auth_token), #Used to bypass all restrictions when getting token
]
