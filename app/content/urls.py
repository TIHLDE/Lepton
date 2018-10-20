from rest_framework import routers
from django.conf.urls import url
from django.conf.urls import include

from .views import ItemViewSet, NewsViewSet, EventViewSet, EventListViewSet, PosterViewSet, GridViewSet, ImageGalleryViewSet, ImageViewSet, WarningViewSet, CategoryViewSet

router = routers.DefaultRouter()

# Register content viewpoints here
router.register('items', ItemViewSet)
router.register('news', NewsViewSet)
router.register('events', EventViewSet, base_name='event')
router.register('eventlist', EventListViewSet)
router.register('posters', PosterViewSet)
router.register('grids', GridViewSet)
router.register('images', ImageViewSet)
router.register('imagegallery', ImageGalleryViewSet)
router.register('warning', WarningViewSet, base_name='warning')
router.register('category', CategoryViewSet)

urlpatterns = [
    url(r'', include(router.urls))
]
