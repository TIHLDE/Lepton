from rest_framework import routers

from .views import ItemViewSet, NewsViewSet, EventViewSet, EventListViewSet, PosterViewSet, GridViewSet, ImageGalleryViewSet, ImageViewSet

router = routers.DefaultRouter()

# Register content viewpoints here
router.register('items', ItemViewSet)
router.register('news', NewsViewSet)
router.register('events', EventViewSet)
router.register('eventlist', EventListViewSet)
router.register('posters', PosterViewSet)
router.register('grids', GridViewSet)
router.register('images', ImageViewSet)
router.register('imagegallery', ImageGalleryViewSet)

urlpatterns = router.urls
