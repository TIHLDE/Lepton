from rest_framework import routers
from django.conf.urls import url
from django.urls import path
from django.conf.urls import include

from .views import (NewsViewSet, EventViewSet, WarningViewSet, CategoryViewSet, accept_form, JobPostViewSet, UserViewSet)

router = routers.DefaultRouter()

# Register content viewpoints here
router.register('news', NewsViewSet)
router.register('events', EventViewSet, base_name='event')
router.register('warning', WarningViewSet, base_name='warning')
router.register('category', CategoryViewSet)
router.register('jobpost', JobPostViewSet, base_name='jobpost')
router.register('user', UserViewSet, base_name='user')

urlpatterns = [
    url(r'', include(router.urls)),
    path('accept-form/', accept_form),
]
