from rest_framework import viewsets

from app.common.mixins import LoggingViewSetMixin


class BaseViewSet(LoggingViewSetMixin, viewsets.ModelViewSet):
    pass
