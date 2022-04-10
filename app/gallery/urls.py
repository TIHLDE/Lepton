from django.urls import include, re_path
from rest_framework import routers

from app.gallery.views.album import AlbumViewSet
from app.gallery.views.picture import PictureViewSet

router = routers.DefaultRouter()
router.register("", AlbumViewSet)
router.register(r"(?P<slug>[^.]+)/pictures", PictureViewSet, basename="pictures")

urlpatterns = [
    re_path(r"", include(router.urls)),
]
