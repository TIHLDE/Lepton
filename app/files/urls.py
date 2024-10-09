from django.urls import include, path
from rest_framework import routers

from app.files.views.file import FileViewSet
from app.files.views.upload import delete, upload
from app.files.views.user_gallery import UserGalleryViewSet

router = routers.DefaultRouter()

router.register("file", FileViewSet, basename="file")
router.register("user_gallery", UserGalleryViewSet, basename="user_gallery")

urlpatterns = [
    path("upload/", upload),
    path("delete-file/<str:container_name>/<str:blob_name>/", delete),
    path("files/", include(router.urls)),
]
