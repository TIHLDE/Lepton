from rest_framework import routers
from django.conf.urls import url
from django.urls import path
from django.conf.urls import include

from .views import (ItemViewSet, NewsViewSet, EventViewSet, EventListViewSet, PosterViewSet,
ImageGalleryViewSet, ImageViewSet, WarningViewSet, CategoryViewSet, auth_password, accept_form, JobPostViewSet)

router = routers.DefaultRouter()

# Register content viewpoints here
router.register('items', ItemViewSet)
router.register('news', NewsViewSet)
router.register('events', EventViewSet, base_name='event')
router.register('eventlist', EventListViewSet)
router.register('posters', PosterViewSet)
router.register('images', ImageViewSet)
router.register('imagegallery', ImageGalleryViewSet)
router.register('warning', WarningViewSet, base_name='warning')
router.register('category', CategoryViewSet)
router.register('jobpost', JobPostViewSet, base_name='jobpost')

urlpatterns = [
    url(r'', include(router.urls)),
    path('authenticate/', auth_password),
    path('accept-form/', accept_form),
]
