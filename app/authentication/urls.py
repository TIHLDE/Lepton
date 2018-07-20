from rest_framework import routers

router = routers.DefaultRouter()

# Register authentication viewsets here 
from django.urls import re_path

from .views import RefreshTokenBlacklistView

urlpatterns = router.urls

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    re_path(r'^token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'^token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^token/blacklist/$', RefreshTokenBlacklistView.as_view(), name='refresh_token_blacklist'),
]
