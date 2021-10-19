from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from app.gallery.views.picture import AlbumViewSet, PictureViewSet

router = routers.DefaultRouter()
router.register("pictures/", PictureViewSet)
router.register("", AlbumViewSet)

urlpatterns = [
    url(r"", include(router.urls)),
]
