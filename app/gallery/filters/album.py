from django_filters.rest_framework import FilterSet

from app.gallery.models.album import Album


class AlbumFilter(FilterSet):
    class Meta:
        model = Album
        fields = ["event"]
