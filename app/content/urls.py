from rest_framework import routers
from django.conf.urls import url
from django.urls import path
from django.conf.urls import include

from rest_framework_swagger.views import get_swagger_view

from .views import NewsViewSet, EventViewSet, WarningViewSet, CategoryViewSet, accept_form, \
    JobPostViewSet, UserViewSet, UserEventViewSet, NotificationViewSet

router = routers.DefaultRouter()

# Register content viewpoints here
router.register('news', NewsViewSet)
router.register('events', EventViewSet, basename='event')
router.register('warning', WarningViewSet, basename='warning')
router.register('category', CategoryViewSet)
router.register('jobpost', JobPostViewSet, basename='jobpost')
router.register('user', UserViewSet, basename='user')
router.register(r'events/(?P<event_id>\d+)/users', UserEventViewSet, basename='user_event')
router.register('notification', NotificationViewSet, basename='notification')

# Swagger
schema_view = get_swagger_view(title='TIHLDE API')


urlpatterns = [
    url(r'docs', schema_view),
    url(r'', include(router.urls)),
    path('accept-form/', accept_form),
]
