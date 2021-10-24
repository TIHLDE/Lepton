class ActionMixin:
    def paginate_response(self, data, serializer, context=None):
        page = self.paginate_queryset(data)
        serializer = serializer(page, many=True, context=context)
        return self.get_paginated_response(serializer.data)
