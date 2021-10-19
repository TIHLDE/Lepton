from rest_framework import serializers


class ActionMixin:
    def paginate_response(self, data, serializer):
        page = self.paginate_queryset(data)
        serializer = serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class OrderedModelSerializerMixin:
    order = serializers.IntegerField(read_only=False, required=True)

    def update(self, instance, validated_data):
        self.do_update_order(instance, validated_data)
        return super().update(instance, validated_data)

    @staticmethod
    def do_update_order(instance, data):
        new_order = data.get("order")
        if new_order and getattr(instance, "order") != new_order:
            instance.to(new_order)
