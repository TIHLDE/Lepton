from django_filters.rest_framework import FilterSet, OrderingFilter

from app.gallery.models.album import Album


class AlbumFilter(FilterSet):
    """Filter and sort albums by date or event."""

    ordering = OrderingFilter(
        fields=(
            "created_at",
            "updated_at",
            "event__title",
        )
    )

    class Meta:
        model = Album
        fields = [
            "event",
        ]
