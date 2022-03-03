from django_filters.rest_framework import FilterSet

from ..models import Cheatsheet


class CheatsheetFilter(FilterSet):
    """Filters cheatsheet by title, course and creator. Works with search query"""

    class Meta:
        model = Cheatsheet
        fields = ["course", "title", "creator"]
