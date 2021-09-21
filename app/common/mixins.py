class ActionMixin:
    def paginate_response(self, data, serializer):
        page = self.paginate_queryset(data)
        serializer = serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
