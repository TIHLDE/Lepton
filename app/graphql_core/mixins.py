from rest_framework import status

from app.forms.mutations import Output


class ListModelMixin:
    @classmethod
    def resolve_list(cls, root, info, **kwargs):
        cls.check_permissions(request=info)
        return cls.get_queryset()


class RetrieveModelMixin:
    @classmethod
    def resolve_retrieve(cls, root, info, **kwargs):
        return cls.get_object(request=info, **kwargs)


class CreateModelMixin(Output):
    """
    Create a model instance.
    """

    @classmethod
    def resolve_mutation(cls, request, *args, **kwargs):
        serializer = cls.get_serializer(data=kwargs)
        serializer.is_valid(raise_exception=True)  # TODO: Proper error message
        cls.perform_create(serializer)
        return cls(serializer.data, message="success", status=status.HTTP_201_CREATED)

    @classmethod
    def perform_create(cls, serializer):
        serializer.save()


# TODO: handle update properly
class MutationMixin:
    @classmethod
    def mutate(cls, root, info, **input):
        return cls.resolve_mutation(root, info, **input)
