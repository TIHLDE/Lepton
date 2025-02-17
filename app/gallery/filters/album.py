from django_filters.rest_framework import FilterSet, OrderingFilter

from app.gallery.models.album import Album


class AlbumFilter(FilterSet):
    """Filter and sort albums by date or event."""

    ordering = OrderingFilter(
        fields=(
        "created_at",
        "updated_at",
        "event",
        "-created_at",
        )
    )

    class Meta:
        model = Album
        fields = [
            "event",
            "-created_at",
        ]

    def get_queryset(self):
        queryset = super().get_queryset()
        order = self.request.query_params.get("order", "desc")
            if order == "asc":
                return queryset.order_by("created_at")
            else:
                return queryset.order_by("-created_at")
        return queryset


