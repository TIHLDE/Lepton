from rest_framework import routers
from django.conf.urls import url
from django.urls import path
from django.conf.urls import include

from rest_framework_swagger.views import get_swagger_view

from .views import (NewsViewSet, EventViewSet, WarningViewSet, CategoryViewSet, accept_form, JobPostViewSet, UserViewSet, UserEventViewSet)

router = routers.DefaultRouter()

# Register content viewpoints here
router.register('news', NewsViewSet)
router.register('events', EventViewSet, base_name='event')
router.register('warning', WarningViewSet, base_name='warning')
router.register('category', CategoryViewSet)
router.register('jobpost', JobPostViewSet, base_name='jobpost')
router.register('user', UserViewSet, base_name='user')
router.register(r'events/(?P<event_id>\d+)/users', UserEventViewSet, base_name='user_event')

# Swagger 
schema_view = get_swagger_view(title='TIHLDE API', url='/api/v1/all')


urlpatterns = [
    url(r'all', schema_view),
    url(r'', include(router.urls)),
    path('accept-form/', accept_form),
]
